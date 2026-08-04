"""Compiled AI — natural language → living, zero-token executable workflow."""

from __future__ import annotations

import json

from app.contracts import CompileRequest, CompileResponse, new_id
from app.zero_copy import get_object_store


STAGES = [
    "template_parse",
    "workspace_provision",
    "code_generation",
    "bundle_build",
    "deploy",
]


class CompilePipeline:
    """Compiler for living software.

    MVP: produce a deterministic artifact JSON describing the provisioned
    workflow. Production: provision DB + agents + edge deploy URL.
    """

    def run(self, req: CompileRequest) -> CompileResponse:
        compile_id = new_id("cmp_")
        completed: list[str] = []
        artifact = {
            "compile_id": compile_id,
            "workflow_name": req.workflow_name,
            "source_prompt": req.natural_language,
            "bindings": req.bindings,
            "runtime": {
                "zero_token": True,
                "trust": "deny_by_default",
                "object_plane": "zero_copy",
            },
            "steps": [],
        }

        for stage in STAGES:
            completed.append(stage)
            artifact["steps"].append({"stage": stage, "status": "ok"})

        # Deterministic live path for kits4kid compiled devotionals
        slug = req.workflow_name.strip().lower().replace(" ", "_")
        live_path = f"/live/{slug}/{compile_id}"
        artifact["live_path"] = live_path

        store = get_object_store()
        ref = store.put(
            json.dumps(artifact, indent=2).encode(),
            media_type="application/json",
            labels={"kind": "compiled_workflow", "workflow": req.workflow_name},
        )

        return CompileResponse(
            compile_id=compile_id,
            status="deployed",
            stages=completed,
            artifact_object_id=ref.object_id,
            live_path=live_path,
            zero_token=True,
        )


def get_compile_pipeline() -> CompilePipeline:
    return CompilePipeline()
