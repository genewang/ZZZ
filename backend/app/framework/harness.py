"""Harness Engineering — tools, jail, validators, Approve gates."""

from __future__ import annotations

from dataclasses import dataclass

from app.contracts import AgentAction, TrustDecision
from app.framework.layers import HarnessSpec
from app.zero_trust import PolicyEngine, PolicyResult, get_policy_engine


@dataclass
class HarnessResult:
    trust: TrustDecision
    reason: str
    audit_event_id: str
    allowed_tools: list[str]


class HarnessRuntime:
    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self.policy = policy or get_policy_engine()

    def bind_session(self, session_id: str, spec: HarnessSpec, *, parent_approved: bool) -> None:
        self.policy.open_session(
            session_id,
            capabilities=spec.capabilities or spec.tools,
            parent_approved=parent_approved,
        )

    def gate(self, session_id: str, action_kind: str, spec: HarnessSpec) -> HarnessResult:
        action = AgentAction(
            kind=action_kind,
            requested_capabilities=spec.capabilities or [action_kind],
            payload={"harness_tools": spec.tools},
        )
        result: PolicyResult = self.policy.evaluate(session_id, action, actor="harness")
        return HarnessResult(
            trust=result.decision,
            reason=result.reason,
            audit_event_id=result.audit.event_id,
            allowed_tools=spec.tools,
        )
