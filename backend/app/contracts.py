from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str = "") -> str:
    raw = uuid4().hex[:12]
    return f"{prefix}{raw}" if prefix else raw


class ModelTier(str, Enum):
    CACHE = "cache"
    LOCAL_SMALL = "local_small"
    LOCAL_LARGE = "local_large"
    FRONTIER = "frontier"
    COMPILED = "compiled"


class IntentClass(str, Enum):
    DEVOTION = "devotion"
    CREATE_3D = "create_3d"
    STORYKEEPER = "storykeeper"
    CHURCH_CURRICULUM = "church_curriculum"
    GENERAL = "general"
    UNSAFE = "unsafe"


class TrustDecision(str, Enum):
    ALLOW = "allow"
    HOLD = "hold"
    DENY = "deny"


class ObjectRef(BaseModel):
    object_id: str
    media_type: str = "application/octet-stream"
    size_bytes: int
    created_at: datetime = Field(default_factory=utcnow)
    labels: dict[str, str] = Field(default_factory=dict)


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: new_id("aud_"))
    ts: datetime = Field(default_factory=utcnow)
    actor: str
    action: str
    decision: TrustDecision
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentAction(BaseModel):
    action_id: str = Field(default_factory=lambda: new_id("act_"))
    kind: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requested_capabilities: list[str] = Field(default_factory=list)


class RouteResult(BaseModel):
    tier: ModelTier
    intent: IntentClass
    cache_hit: bool = False
    similarity: float | None = None
    model_id: str
    tokens_billed: int = 0
    latency_ms: int = 0
    compiled_path: str | None = None


class InferenceRequest(BaseModel):
    session_id: str
    prompt: str
    parent_approved: bool = False
    age_band: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    context_object_ids: list[str] = Field(default_factory=list)


class InferenceResponse(BaseModel):
    request_id: str
    output: str
    route: RouteResult
    trust: TrustDecision
    audit_event_id: str
    object_ids: list[str] = Field(default_factory=list)


class CreateSceneRequest(BaseModel):
    session_id: str
    mode: str = "text"  # text | sketch
    prompt: str
    preset_tag: str | None = None
    parent_approved: bool = False
    age_band: str = "5-8"


class CreateSceneResponse(BaseModel):
    scene_id: str
    status: str
    title: str
    mesh_object_id: str | None = None
    printable: bool = False
    route: RouteResult
    trust: TrustDecision
    requires_parent_approve: bool = True
    audit_event_id: str


class CompileRequest(BaseModel):
    workflow_name: str
    natural_language: str
    bindings: dict[str, str] = Field(default_factory=dict)


class CompileResponse(BaseModel):
    compile_id: str
    status: str
    stages: list[str]
    artifact_object_id: str | None = None
    live_path: str | None = None
    zero_token: bool = True
