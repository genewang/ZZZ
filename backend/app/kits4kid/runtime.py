"""kits4kid vertical — thin product surface on the reusable Triple Zero engine."""

from __future__ import annotations

import json

from app.contracts import (
    AgentAction,
    CreateSceneRequest,
    CreateSceneResponse,
    InferenceRequest,
    InferenceResponse,
    ModelTier,
    TrustDecision,
    new_id,
)
from app.framework import EngineRequest, get_engine
from app.vllm import get_vllm_router
from app.zero_copy import get_object_store
from app.zero_trust import get_policy_engine


class Kits4KidRuntime:
    def __init__(self) -> None:
        self.store = get_object_store()
        self.router = get_vllm_router()
        self.policy = get_policy_engine()
        self.engine = get_engine()

    def inference(self, req: InferenceRequest) -> InferenceResponse:
        result = self.engine.run(
            EngineRequest(
                session_id=req.session_id,
                vertical="kits4kid",
                user_input=req.prompt,
                template_id="kits4kid.devotion",
                graph_id=None,
                parent_approved=req.parent_approved,
                object_ids=req.context_object_ids,
                metadata={"age_band": req.age_band or "5-8"},
            )
        )
        head_route = self.router.route(req.prompt)
        return InferenceResponse(
            request_id=result.run_id,
            output=result.output,
            route=head_route.route.model_copy(
                update={
                    "cache_hit": result.cache_hit,
                    "tokens_billed": result.tokens_billed,
                    "compiled_path": result.compiled_path,
                    "model_id": result.model or head_route.route.model_id,
                }
            ),
            trust=TrustDecision(result.trust),
            audit_event_id=result.flywheel_event_id or new_id("aud_"),
            object_ids=result.object_ids,
        )

    def create_scene(self, req: CreateSceneRequest) -> CreateSceneResponse:
        self.policy.open_session(
            req.session_id,
            capabilities=["generate_scene_draft", "export_mesh"],
            parent_approved=req.parent_approved,
        )

        # Multi-agent graph: creator head → critic head on vLLM
        engine_result = self.engine.run(
            EngineRequest(
                session_id=req.session_id,
                vertical="kits4kid",
                user_input=req.prompt,
                graph_id="kits4kid.create_and_check",
                parent_approved=req.parent_approved,
                metadata={"age_band": req.age_band, "mode": req.mode},
            )
        )

        head_route = self.router.route(
            req.prompt,
            prefer_compiled="sprout_noah_create" if "noah" in req.prompt.lower() else None,
        )
        route = head_route.route
        scene_id = new_id("scn_")
        title = (req.preset_tag or req.prompt[:48] or "Untitled scene").strip()

        mesh_doc = {
            "scene_id": scene_id,
            "title": title,
            "prompt": req.prompt,
            "age_band": req.age_band,
            "watertight": True,
            "manifold": True,
            "style": "kid_friendly",
            "agent_output": engine_result.output,
            "graph_path": engine_result.graph_path,
            "vllm_head": engine_result.head_id,
            "route_tier": route.tier.value,
        }
        mesh_ref = self.store.put(
            json.dumps(mesh_doc).encode(),
            media_type="application/json",
            labels={"kind": "mesh_draft", "scene": scene_id},
        )

        export_action = AgentAction(
            kind="export_mesh",
            payload={"mesh_object_id": mesh_ref.object_id},
            requested_capabilities=["export_mesh"],
        )
        export_trust = self.policy.evaluate(req.session_id, export_action, actor="create_studio")

        if export_trust.decision == TrustDecision.HOLD:
            return CreateSceneResponse(
                scene_id=scene_id,
                status="awaiting_parent_approve",
                title=title,
                mesh_object_id=mesh_ref.object_id,
                printable=False,
                route=route,
                trust=TrustDecision.HOLD,
                requires_parent_approve=True,
                audit_event_id=export_trust.audit.event_id,
            )

        if export_trust.decision == TrustDecision.DENY:
            return CreateSceneResponse(
                scene_id=scene_id,
                status="denied",
                title=title,
                mesh_object_id=None,
                printable=False,
                route=route,
                trust=TrustDecision.DENY,
                requires_parent_approve=True,
                audit_event_id=export_trust.audit.event_id,
            )

        if route.tier != ModelTier.CACHE:
            self.router.remember(req.prompt, json.dumps(mesh_doc), route.intent)

        return CreateSceneResponse(
            scene_id=scene_id,
            status="printable",
            title=title,
            mesh_object_id=mesh_ref.object_id,
            printable=True,
            route=route,
            trust=TrustDecision.ALLOW,
            requires_parent_approve=False,
            audit_event_id=export_trust.audit.event_id,
        )

    def approve(self, session_id: str) -> dict[str, str | bool]:
        self.policy.set_parent_approved(session_id, True)
        return {"session_id": session_id, "parent_approved": True}


def get_runtime() -> Kits4KidRuntime:
    return Kits4KidRuntime()
