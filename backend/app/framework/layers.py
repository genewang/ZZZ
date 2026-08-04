"""Reusable Triple Zero engineering stack.

Layer progression (outer → inner compounding):

  Prompt → Context → Harness → Loop → Graph → Flywheel

Each layer is vertical-agnostic. kits4kid is one registered product surface
on top of the same kernel + vLLM multi-head fabric.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EngineeringLayer(str, Enum):
    PROMPT = "prompt"
    CONTEXT = "context"
    HARNESS = "harness"
    LOOP = "loop"
    GRAPH = "graph"
    FLYWHEEL = "flywheel"


LAYER_ORDER: tuple[EngineeringLayer, ...] = (
    EngineeringLayer.PROMPT,
    EngineeringLayer.CONTEXT,
    EngineeringLayer.HARNESS,
    EngineeringLayer.LOOP,
    EngineeringLayer.GRAPH,
    EngineeringLayer.FLYWHEEL,
)


class LayerBrief(BaseModel):
    layer: EngineeringLayer
    purpose: str
    owns: list[str]
    feeds: EngineeringLayer | None = None


ARCHITECTURE_BRIEF: list[LayerBrief] = [
    LayerBrief(
        layer=EngineeringLayer.PROMPT,
        purpose="Shape intent into durable, testable prompt artifacts",
        owns=["templates", "system packs", "few-shot libraries", "output schemas"],
        feeds=EngineeringLayer.CONTEXT,
    ),
    LayerBrief(
        layer=EngineeringLayer.CONTEXT,
        purpose="Assemble the right evidence without copying payloads",
        owns=["retrieval", "zero-copy refs", "window packing", "session memory"],
        feeds=EngineeringLayer.HARNESS,
    ),
    LayerBrief(
        layer=EngineeringLayer.HARNESS,
        purpose="Bound execution: tools, jail, evals, parent gates",
        owns=["tool registry", "WASM/policy jail", "validators", "Approve gates"],
        feeds=EngineeringLayer.LOOP,
    ),
    LayerBrief(
        layer=EngineeringLayer.LOOP,
        purpose="Iterate to an outcome under budget",
        owns=["retry/critique", "tool-call loops", "token budgets", "stop criteria"],
        feeds=EngineeringLayer.GRAPH,
    ),
    LayerBrief(
        layer=EngineeringLayer.GRAPH,
        purpose="Orchestrate multi-agent / multi-head workflows",
        owns=["agent DAGs", "head affinity", "handoffs", "shared object plane"],
        feeds=EngineeringLayer.FLYWHEEL,
    ),
    LayerBrief(
        layer=EngineeringLayer.FLYWHEEL,
        purpose="Capture action data and compound quality + Zero-Token compiles",
        owns=["traces", "labelling", "eval suites", "compiled paths"],
        feeds=None,
    ),
]


class PromptArtifact(BaseModel):
    template_id: str
    system: str
    user_template: str
    few_shots: list[dict[str, str]] = Field(default_factory=list)
    output_schema: dict[str, Any] | None = None
    tags: list[str] = Field(default_factory=list)


class ContextPack(BaseModel):
    object_ids: list[str] = Field(default_factory=list)
    snippets: list[str] = Field(default_factory=list)
    memory_keys: list[str] = Field(default_factory=list)
    token_budget: int = 4096
    packed_text: str = ""


class HarnessSpec(BaseModel):
    tools: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    require_parent_approve: bool = False
    validators: list[str] = Field(default_factory=list)
    max_tool_calls: int = 8


class LoopPolicy(BaseModel):
    max_iters: int = 3
    critique: bool = True
    stop_on_trust_hold: bool = True
    token_budget: int = 2048


class GraphNodeSpec(BaseModel):
    node_id: str
    agent_id: str
    head_id: str
    prompt_template_id: str
    harness: HarnessSpec = Field(default_factory=HarnessSpec)
    loop: LoopPolicy = Field(default_factory=LoopPolicy)


class GraphSpec(BaseModel):
    graph_id: str
    nodes: list[GraphNodeSpec]
    edges: list[tuple[str, str]] = Field(default_factory=list)
    entry: str


class FlywheelEvent(BaseModel):
    kind: str
    session_id: str
    prompt: str
    output: str
    head_id: str | None = None
    route_tier: str | None = None
    trust: str | None = None
    corrections: dict[str, Any] = Field(default_factory=dict)
    outcome: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngineRequest(BaseModel):
    """Vertical-agnostic run request through the six layers."""

    session_id: str
    vertical: str = "default"
    user_input: str
    template_id: str | None = None
    graph_id: str | None = None
    parent_approved: bool = False
    object_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngineResponse(BaseModel):
    run_id: str
    layers_touched: list[EngineeringLayer]
    output: str
    head_id: str | None = None
    model: str | None = None
    tokens_billed: int = 0
    cache_hit: bool = False
    compiled_path: str | None = None
    trust: str
    object_ids: list[str] = Field(default_factory=list)
    graph_path: list[str] = Field(default_factory=list)
    flywheel_event_id: str | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)
