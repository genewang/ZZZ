"""Unified engine: Prompt → Context → Harness → Loop → Graph → Flywheel."""

from __future__ import annotations

from app.contracts import ModelTier, TrustDecision, new_id
from app.framework.context import ContextEngine
from app.framework.flywheel import FlywheelEngine
from app.framework.graph import (
    GraphEngine,
    default_devotion_graph,
    default_kits4kid_graph,
)
from app.framework.harness import HarnessRuntime
from app.framework.layers import (
    ARCHITECTURE_BRIEF,
    EngineeringLayer,
    EngineRequest,
    EngineResponse,
    FlywheelEvent,
    HarnessSpec,
    LoopPolicy,
)
from app.framework.loop import LoopEngine
from app.framework.prompt import PromptLibrary, build_default_prompts
from app.vllm import get_vllm_pool, get_vllm_router


class TripleZeroEngine:
    """Reusable multi-agent / multi-head runtime on vLLM + Triple Zero."""

    def __init__(self) -> None:
        self.prompts = build_default_prompts()
        self.context = ContextEngine()
        self.harness = HarnessRuntime()
        self.pool = get_vllm_pool()
        self.router = get_vllm_router()
        self.loops = LoopEngine(pool=self.pool, prompts=self.prompts)
        self.graphs = GraphEngine(self.prompts, self.context, self.harness, self.loops)
        self.flywheel = FlywheelEngine()
        self.graphs.register(default_kits4kid_graph())
        self.graphs.register(default_devotion_graph())

    def architecture(self) -> dict:
        return {
            "layers": [b.model_dump() for b in ARCHITECTURE_BRIEF],
            "vllm_heads": [h.model_dump() for h in self.pool.list_heads()],
            "graphs": list(self.graphs._graphs.keys()),
            "prompt_templates": self.prompts.list_ids(),
        }

    def run(self, req: EngineRequest) -> EngineResponse:
        run_id = new_id("run_")
        layers: list[EngineeringLayer] = [
            EngineeringLayer.PROMPT,
            EngineeringLayer.CONTEXT,
            EngineeringLayer.HARNESS,
        ]

        # Graph path (multi-agent)
        if req.graph_id:
            layers.extend(
                [EngineeringLayer.LOOP, EngineeringLayer.GRAPH, EngineeringLayer.FLYWHEEL]
            )
            graph_result = self.graphs.run(
                req.graph_id,
                session_id=req.session_id,
                user_input=req.user_input,
                parent_approved=req.parent_approved,
                object_ids=req.object_ids,
                vars={
                    "age_band": str(req.metadata.get("age_band", "5-8")),
                    "mode": str(req.metadata.get("mode", "text")),
                },
            )
            # Final node output
            output = ""
            if graph_result.path:
                output = graph_result.outputs.get(graph_result.path[-1], "")
            head_id = graph_result.head_ids.get(graph_result.path[-1]) if graph_result.path else None
            fw_id = self.flywheel.record(
                FlywheelEvent(
                    kind="graph_run",
                    session_id=req.session_id,
                    prompt=req.user_input,
                    output=output,
                    head_id=head_id,
                    trust=graph_result.trust.value,
                    outcome="hold" if graph_result.trust == TrustDecision.HOLD else "ok",
                    metadata={"graph_id": req.graph_id, "path": graph_result.path},
                )
            )
            self.context.remember(req.session_id, output[:400])
            return EngineResponse(
                run_id=run_id,
                layers_touched=layers,
                output=output,
                head_id=head_id,
                model=self.pool.get(head_id).model if head_id else None,
                tokens_billed=graph_result.tokens_billed,
                trust=graph_result.trust.value,
                object_ids=graph_result.object_ids,
                graph_path=graph_result.path,
                flywheel_event_id=fw_id,
                diagnostics={"vertical": req.vertical, "mode": "graph"},
            )

        # Single-shot MoM path via vLLM semantic router
        layers.extend([EngineeringLayer.LOOP, EngineeringLayer.FLYWHEEL])
        template_id = req.template_id or "generic.reason"
        age = str(req.metadata.get("age_band", "5-8"))
        mode = str(req.metadata.get("mode", "text"))
        system, user = self.prompts.render(
            template_id,
            user_input=req.user_input,
            age_band=age,
            mode=mode,
            draft=req.user_input,
            workflow_name=req.vertical,
        )

        ctx = self.context.assemble(
            session_id=req.session_id,
            user_input=user,
            object_ids=req.object_ids,
        )

        harness = HarnessSpec(
            tools=["read_scripture", "speak_devotion", "generate_scene_draft"],
            capabilities=["read_scripture", "speak_devotion", "generate_scene_draft"],
            require_parent_approve=True,
        )
        self.harness.bind_session(req.session_id, harness, parent_approved=req.parent_approved)
        action_kind = "speak_devotion" if req.parent_approved else "generate_scene_draft"
        gate = self.harness.gate(req.session_id, action_kind, harness)

        head_route = self.router.route(req.user_input)
        route = head_route.route

        if route.intent.value == "unsafe" or gate.trust == TrustDecision.DENY:
            fw_id = self.flywheel.record(
                FlywheelEvent(
                    kind="denied",
                    session_id=req.session_id,
                    prompt=req.user_input,
                    output="",
                    trust=TrustDecision.DENY.value,
                    outcome="denied",
                )
            )
            return EngineResponse(
                run_id=run_id,
                layers_touched=layers,
                output="Blocked by Zero-Trust policy.",
                head_id=head_route.head.head_id,
                model=head_route.head.model,
                trust=TrustDecision.DENY.value,
                flywheel_event_id=fw_id,
            )

        if route.cache_hit and head_route.cached_output is not None:
            output = head_route.cached_output
            tokens = 0
            model = "semantic-cache"
            head_id = head_route.head.head_id
        elif route.tier == ModelTier.COMPILED and head_route.compiled_output is not None:
            output = head_route.compiled_output
            tokens = 0
            model = "compiled-ai"
            head_id = head_route.head.head_id
        else:
            loop_result = self.loops.run(
                head_id=head_route.head.head_id,
                system=system,
                user=ctx.packed_text,
                policy=LoopPolicy(max_iters=2, critique=True),
            )
            output = loop_result.output
            tokens = sum(c.total_tokens or c.completion_tokens for c in loop_result.completions)
            model = head_route.head.model
            head_id = head_route.head.head_id
            if gate.trust == TrustDecision.ALLOW:
                self.router.remember(req.user_input, output, route.intent)

        trust = gate.trust
        fw_id = self.flywheel.record(
            FlywheelEvent(
                kind="inference",
                session_id=req.session_id,
                prompt=req.user_input,
                output=output,
                head_id=head_id,
                route_tier=route.tier.value,
                trust=trust.value,
                outcome="hold" if trust == TrustDecision.HOLD else "ok",
            )
        )
        self.context.remember(req.session_id, output[:400])

        return EngineResponse(
            run_id=run_id,
            layers_touched=layers,
            output=output,
            head_id=head_id,
            model=model,
            tokens_billed=tokens if not route.cache_hit and route.tier != ModelTier.COMPILED else 0,
            cache_hit=route.cache_hit,
            compiled_path=route.compiled_path,
            trust=trust.value,
            object_ids=ctx.object_ids,
            flywheel_event_id=fw_id,
            diagnostics={
                "vertical": req.vertical,
                "intent": route.intent.value,
                "vllm_stub": False,
                "mode": "mom",
            },
        )


_engine: TripleZeroEngine | None = None


def get_engine() -> TripleZeroEngine:
    global _engine
    if _engine is None:
        _engine = TripleZeroEngine()
    return _engine
