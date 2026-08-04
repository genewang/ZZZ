"""Loop Engineering — budgeted generate → critique → refine cycles on vLLM heads."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.framework.layers import LoopPolicy
from app.framework.prompt import PromptLibrary
from app.vllm import ChatMessage, VLLMCompletion, VLLMHeadPool, get_vllm_pool


@dataclass
class LoopResult:
    output: str
    iters: int
    completions: list[VLLMCompletion] = field(default_factory=list)
    stopped_reason: str = "max_iters"


class LoopEngine:
    def __init__(
        self,
        pool: VLLMHeadPool | None = None,
        prompts: PromptLibrary | None = None,
    ) -> None:
        self.pool = pool or get_vllm_pool()
        self.prompts = prompts

    def run(
        self,
        *,
        head_id: str,
        system: str,
        user: str,
        policy: LoopPolicy,
        critic_head_id: str = "critic",
    ) -> LoopResult:
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user),
        ]
        completions: list[VLLMCompletion] = []
        output = ""
        for i in range(policy.max_iters):
            completion = self.pool.chat(head_id, messages, max_tokens=min(512, policy.token_budget))
            completions.append(completion)
            output = completion.content
            if not policy.critique or i == policy.max_iters - 1:
                return LoopResult(
                    output=output,
                    iters=i + 1,
                    completions=completions,
                    stopped_reason="complete" if not policy.critique else "max_iters",
                )

            critic_messages = [
                ChatMessage(
                    role="system",
                    content=(
                        self.prompts.get("critic.pass").system
                        if self.prompts
                        else "Reply PASS or FIX."
                    ),
                ),
                ChatMessage(role="user", content=f"Draft:\n{output}"),
            ]
            critique = self.pool.chat(critic_head_id, critic_messages, max_tokens=200)
            completions.append(critique)
            if critique.content.strip().upper().startswith("PASS"):
                return LoopResult(
                    output=output,
                    iters=i + 1,
                    completions=completions,
                    stopped_reason="critique_pass",
                )
            messages.append(ChatMessage(role="assistant", content=output))
            messages.append(
                ChatMessage(
                    role="user",
                    content=f"Revise based on critique:\n{critique.content}",
                )
            )

        return LoopResult(output=output, iters=policy.max_iters, completions=completions)
