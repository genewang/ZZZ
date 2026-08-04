"""Prompt Engineering — templates, system packs, few-shots, schemas."""

from __future__ import annotations

from app.framework.layers import PromptArtifact


class PromptLibrary:
    def __init__(self) -> None:
        self._templates: dict[str, PromptArtifact] = {}

    def register(self, artifact: PromptArtifact) -> None:
        self._templates[artifact.template_id] = artifact

    def get(self, template_id: str) -> PromptArtifact:
        if template_id not in self._templates:
            raise KeyError(f"Unknown prompt template: {template_id}")
        return self._templates[template_id]

    def render(self, template_id: str, **vars: str) -> tuple[str, str]:
        art = self.get(template_id)
        user = art.user_template.format(**vars)
        return art.system, user

    def list_ids(self) -> list[str]:
        return sorted(self._templates)


def build_default_prompts() -> PromptLibrary:
    lib = PromptLibrary()
    lib.register(
        PromptArtifact(
            template_id="generic.reason",
            system="You are a careful assistant. Be concise and actionable.",
            user_template="{user_input}",
            tags=["general"],
        )
    )
    lib.register(
        PromptArtifact(
            template_id="kits4kid.devotion",
            system=(
                "You craft age-fit Bible devotionals. Warm, concrete, parent-safe. "
                "Never unsupervised spiritual counsel beyond the age band."
            ),
            user_template="Age band: {age_band}\nRequest: {user_input}",
            few_shots=[
                {
                    "user": "Mustard seed for age 5",
                    "assistant": "Tiny seed, big trust — one sentence story + one craft cue.",
                }
            ],
            tags=["devotion", "kits4kid"],
        )
    )
    lib.register(
        PromptArtifact(
            template_id="kits4kid.create3d",
            system=(
                "You specify kid-safe printable 3D Bible scenes: watertight, soft forms, "
                "no weapons realism. Output a short mesh brief."
            ),
            user_template="Mode: {mode}\nAge: {age_band}\nScene: {user_input}",
            tags=["create_3d", "kits4kid"],
        )
    )
    lib.register(
        PromptArtifact(
            template_id="critic.pass",
            system="Critique the draft for safety, age-fit, and completeness. Reply with PASS or FIX: <notes>.",
            user_template="Draft:\n{draft}",
            tags=["critique"],
        )
    )
    lib.register(
        PromptArtifact(
            template_id="compile.workflow",
            system="Compile the workflow into deterministic steps with zero ongoing token cost for core paths.",
            user_template="Workflow: {workflow_name}\nSpec: {user_input}",
            tags=["compile"],
        )
    )
    return lib
