from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_kernel():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["kernel"]["vllm_heads"] >= 6


def test_architecture_six_layers():
    res = client.get("/v1/architecture")
    assert res.status_code == 200
    body = res.json()
    layers = [item["layer"] for item in body["layers"]]
    assert layers == [
        "prompt",
        "context",
        "harness",
        "loop",
        "graph",
        "flywheel",
    ]
    assert len(body["vllm_heads"]) >= 6
    assert "kits4kid.create_and_check" in body["graphs"]


def test_engine_mom_run():
    res = client.post(
        "/v1/engine/run",
        json={
            "session_id": "eng1",
            "vertical": "kits4kid",
            "user_input": "age 5 bedtime Exodus story",
            "template_id": "kits4kid.devotion",
            "parent_approved": True,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "prompt" in body["layers_touched"]
    assert "flywheel" in body["layers_touched"]
    assert body["trust"] in {"allow", "hold"}
    assert body["compiled_path"] == "age5_exodus_bedtime" or body["cache_hit"] or body["output"]


def test_engine_graph_multi_agent():
    res = client.post(
        "/v1/engine/run",
        json={
            "session_id": "eng_graph",
            "vertical": "kits4kid",
            "user_input": "Noah's ark printable soft toy",
            "graph_id": "kits4kid.create_and_check",
            "parent_approved": True,
            "metadata": {"age_band": "5-8", "mode": "text"},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "graph" in body["layers_touched"]
    assert body["graph_path"]
    assert body["head_id"] in {"creator", "critic"}


def test_create_scene_holds_without_parent_approve():
    res = client.post(
        "/v1/create/scene",
        json={
            "session_id": "sess_demo_1",
            "prompt": "Noah's ark on a misty mountain, kid-friendly, printable",
            "preset_tag": "Noah's Ark",
            "parent_approved": False,
            "age_band": "5-8",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["trust"] == "hold"
    assert body["status"] == "awaiting_parent_approve"
    assert body["printable"] is False
    assert body["mesh_object_id"]


def test_create_scene_printable_after_approve():
    session = "sess_demo_2"
    client.post(f"/v1/sessions/{session}/approve")
    res = client.post(
        "/v1/create/scene",
        json={
            "session_id": session,
            "prompt": "David's sling and five smooth stones",
            "preset_tag": "David's Sling",
            "parent_approved": True,
            "age_band": "5-8",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["trust"] == "allow"
    assert body["printable"] is True


def test_compile_living_software():
    res = client.post(
        "/v1/compile",
        json={
            "workflow_name": "sprout_monthly_devotion",
            "natural_language": "Compile a monthly Sprout devotion with Create Studio prompt",
            "bindings": {"kit_line": "sprout"},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "deployed"
    assert body["zero_token"] is True


def test_semantic_cache_second_hit():
    payload = {
        "session_id": "sess_cache",
        "prompt": "Bible devotion about the mustard seed parable for kids",
        "parent_approved": True,
        "capabilities": ["read_scripture", "speak_devotion"],
    }
    first = client.post("/v1/inference", json=payload)
    assert first.status_code == 200
    second = client.post("/v1/inference", json=payload)
    assert second.status_code == 200
    assert second.json()["route"]["cache_hit"] is True
    assert second.json()["route"]["tokens_billed"] == 0
