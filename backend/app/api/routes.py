from fastapi import APIRouter

from app.compile.pipeline import get_compile_pipeline
from app.contracts import (
    CompileRequest,
    CompileResponse,
    CreateSceneRequest,
    CreateSceneResponse,
    InferenceRequest,
    InferenceResponse,
)
from app.framework import EngineRequest, EngineResponse, get_engine
from app.kits4kid.runtime import get_runtime
from app.vllm import get_vllm_pool, get_vllm_router
from app.zero_copy import get_object_store
from app.zero_trust import WasmJail, get_policy_engine

router = APIRouter()


@router.get("/health")
def health() -> dict:
    pool = get_vllm_pool()
    mom = get_vllm_router()
    return {
        "status": "ok",
        "kernel": {
            "zero_copy": get_object_store().__class__.__name__,
            "zero_trust": WasmJail().describe(),
            "zero_token": mom.cache.stats(),
            "vllm_heads": len(pool.list_heads()),
        },
    }


@router.get("/v1/architecture")
def architecture() -> dict:
    return get_engine().architecture()


@router.get("/v1/vllm/heads")
def vllm_heads() -> dict:
    pool = get_vllm_pool()
    return {
        "heads": [h.model_dump() for h in pool.list_heads()],
        "health": [h.__dict__ for h in pool.health()],
    }


@router.post("/v1/engine/run", response_model=EngineResponse)
def engine_run(body: EngineRequest) -> EngineResponse:
    """Vertical-agnostic entry: Prompt→Context→Harness→Loop→Graph→Flywheel."""
    return get_engine().run(body)


@router.post("/v1/inference", response_model=InferenceResponse)
def inference(body: InferenceRequest) -> InferenceResponse:
    return get_runtime().inference(body)


@router.post("/v1/create/scene", response_model=CreateSceneResponse)
def create_scene(body: CreateSceneRequest) -> CreateSceneResponse:
    return get_runtime().create_scene(body)


@router.post("/v1/sessions/{session_id}/approve")
def approve_session(session_id: str) -> dict:
    return get_runtime().approve(session_id)


@router.post("/v1/compile", response_model=CompileResponse)
def compile_workflow(body: CompileRequest) -> CompileResponse:
    return get_compile_pipeline().run(body)


@router.get("/v1/flywheel")
def flywheel(limit: int = 50) -> dict:
    fw = get_engine().flywheel
    return {
        "stats": fw.stats.__dict__,
        "events": [e.model_dump() for e in fw.recent(limit)],
        "compile_candidates": fw.compile_candidates(),
    }


@router.get("/v1/audit")
def audit(limit: int = 50) -> dict:
    events = get_policy_engine().recent_audit(limit=limit)
    return {"events": [e.model_dump(mode="json") for e in events]}


@router.get("/v1/objects/{object_id}")
def get_object_meta(object_id: str) -> dict:
    ref = get_object_store().get_ref(object_id)
    return ref.model_dump(mode="json")
