"""Graph Engineering — multi-agent DAGs with vLLM head affinity."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.framework.layers import GraphSpec, HarnessSpec, LoopPolicy, GraphNodeSpec
from app.framework.context import ContextEngine
from app.framework.harness import HarnessRuntime
from app.framework.loop import LoopEngine
from app.framework.prompt import PromptLibrary
from app.contracts import TrustDecision


@dataclass
class GraphRunResult:
    outputs: dict[str, str] = field(default_factory=dict)
    path: list[str] = field(default_factory=list)
    head_ids: dict[str, str] = field(default_factory=dict)
    trust: TrustDecision = TrustDecision.ALLOW
    tokens_billed: int = 0
    object_ids: list[str] = field(default_factory=list)


class GraphEngine:
    def __init__(
        self,
        prompts: PromptLibrary,
        context: ContextEngine,
        harness: HarnessRuntime,
        loops: LoopEngine,
    ) -> None:
        self.prompts = prompts
        self.context = context
        self.harness = harness
        self.loops = loops
        self._graphs: dict[str, GraphSpec] = {}

    def register(self, graph: GraphSpec) -> None:
        self._graphs[graph.graph_id] = graph

    def get(self, graph_id: str) -> GraphSpec:
        if graph_id not in self._graphs:
            raise KeyError(f"Unknown graph: {graph_id}")
        return self._graphs[graph_id]

    def run(
        self,
        graph_id: str,
        *,
        session_id: str,
        user_input: str,
        parent_approved: bool,
        object_ids: list[str] | None = None,
        vars: dict[str, str] | None = None,
    ) -> GraphRunResult:
        graph = self.get(graph_id)
        nodes = {n.node_id: n for n in graph.nodes}
        adj: dict[str, list[str]] = {n.node_id: [] for n in graph.nodes}
        for a, b in graph.edges:
            adj[a].append(b)

        result = GraphRunResult()
        queue = [graph.entry]
        visited: set[str] = set()
        render_vars = {"user_input": user_input, "age_band": "5-8", "mode": "text"}
        if vars:
            render_vars.update(vars)

        ctx = self.context.assemble(
            session_id=session_id,
            user_input=user_input,
            object_ids=object_ids,
        )
        result.object_ids = list(ctx.object_ids)

        while queue:
            node_id = queue.pop(0)
            if node_id in visited or node_id not in nodes:
                continue
            visited.add(node_id)
            node = nodes[node_id]

            if result.path:
                prev = result.path[-1]
                render_vars["draft"] = result.outputs.get(prev, user_input)
            else:
                render_vars["draft"] = user_input

            result.path.append(node_id)
            result.head_ids[node_id] = node.head_id

            self.harness.bind_session(session_id, node.harness, parent_approved=parent_approved)
            gate = self.harness.gate(session_id, node.harness.tools[0] if node.harness.tools else "generate_scene_draft", node.harness)
            if gate.trust == TrustDecision.DENY:
                result.trust = TrustDecision.DENY
                result.outputs[node_id] = "Denied by harness."
                break
            if gate.trust == TrustDecision.HOLD and node.loop.stop_on_trust_hold:
                result.trust = TrustDecision.HOLD
                # Still produce a draft via loop for quarantine
            system, user = self.prompts.render(node.prompt_template_id, **render_vars)
            user = f"{ctx.packed_text}\n\n---\nTask:\n{user}"
            loop_result = self.loops.run(
                head_id=node.head_id,
                system=system,
                user=user,
                policy=node.loop,
            )
            result.outputs[node_id] = loop_result.output
            result.tokens_billed += sum(c.total_tokens or c.completion_tokens for c in loop_result.completions)
            if result.trust == TrustDecision.HOLD:
                break
            queue.extend(adj.get(node_id, []))

        return result


def default_kits4kid_graph() -> GraphSpec:
    return GraphSpec(
        graph_id="kits4kid.create_and_check",
        entry="create",
        nodes=[
            GraphNodeSpec(
                node_id="create",
                agent_id="create_studio",
                head_id="creator",
                prompt_template_id="kits4kid.create3d",
                harness=HarnessSpec(
                    tools=["generate_scene_draft", "export_mesh"],
                    capabilities=["generate_scene_draft", "export_mesh"],
                    require_parent_approve=True,
                ),
                loop=LoopPolicy(max_iters=2, critique=True, stop_on_trust_hold=False),
            ),
            GraphNodeSpec(
                node_id="critic",
                agent_id="safety_critic",
                head_id="critic",
                prompt_template_id="critic.pass",
                harness=HarnessSpec(
                    tools=["generate_scene_draft"],
                    capabilities=["generate_scene_draft"],
                ),
                loop=LoopPolicy(max_iters=1, critique=False),
            ),
        ],
        edges=[("create", "critic")],
    )


def default_devotion_graph() -> GraphSpec:
    return GraphSpec(
        graph_id="kits4kid.devotion",
        entry="devote",
        nodes=[
            GraphNodeSpec(
                node_id="devote",
                agent_id="devotion_agent",
                head_id="reasoner_small",
                prompt_template_id="kits4kid.devotion",
                harness=HarnessSpec(
                    tools=["speak_devotion", "read_scripture"],
                    capabilities=["speak_devotion", "read_scripture"],
                    require_parent_approve=True,
                ),
                loop=LoopPolicy(max_iters=2, critique=True),
            )
        ],
        edges=[],
    )
