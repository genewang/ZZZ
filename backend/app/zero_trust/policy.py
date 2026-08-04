"""Zero-Trust policy engine — deny-by-default with parent Approve gates.

Production target: Rust supervisor + WASM sandbox (AgentZero / Wassette).
Local default: capability ACL + audit log that mirrors the jail contract.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from app.config import Settings, get_settings
from app.contracts import AgentAction, AuditEvent, TrustDecision, new_id


# Capabilities an agent may request. Anything else is denied.
ALLOWED_CAPABILITIES = frozenset(
    {
        "read_scripture",
        "generate_scene_draft",
        "speak_devotion",
        "export_mesh",
        "storykeeper_draft",
        "church_share_prompt",
    }
)

# Actions that always require an explicit parent Approve signal.
PARENT_GATED_ACTIONS = frozenset(
    {
        "speak_devotion",
        "export_mesh",
        "publish_scene",
        "storykeeper_release",
    }
)

# Hard denies — structurally impossible in the jail.
HARD_DENY_ACTIONS = frozenset(
    {
        "open_web",
        "exfiltrate",
        "shell_exec",
        "unscoped_chat",
        "raw_media_export",
    }
)


@dataclass
class PolicyResult:
    decision: TrustDecision
    reason: str
    audit: AuditEvent


@dataclass
class JailSession:
    session_id: str
    granted: set[str] = field(default_factory=set)
    tool_calls: int = 0
    parent_approved: bool = False


class PolicyEngine:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._lock = threading.RLock()
        self._sessions: dict[str, JailSession] = {}
        self._audit: list[AuditEvent] = []

    def open_session(
        self,
        session_id: str,
        *,
        capabilities: list[str] | None = None,
        parent_approved: bool = False,
    ) -> JailSession:
        granted = set(capabilities or []) & ALLOWED_CAPABILITIES
        session = JailSession(
            session_id=session_id,
            granted=granted,
            parent_approved=parent_approved,
        )
        with self._lock:
            self._sessions[session_id] = session
        return session

    def set_parent_approved(self, session_id: str, approved: bool = True) -> None:
        with self._lock:
            session = self._sessions.setdefault(session_id, JailSession(session_id=session_id))
            session.parent_approved = approved

    def evaluate(self, session_id: str, action: AgentAction, actor: str = "agent") -> PolicyResult:
        with self._lock:
            session = self._sessions.setdefault(session_id, JailSession(session_id=session_id))
            session.tool_calls += 1

            if self.settings.deny_by_default is False:
                # Still enforce hard denies even if deny-by-default is relaxed.
                pass

            if action.kind in HARD_DENY_ACTIONS:
                return self._decide(
                    actor,
                    action.kind,
                    TrustDecision.DENY,
                    "Hard deny — capability structurally impossible in jail",
                    {"action_id": action.action_id},
                )

            if session.tool_calls > self.settings.max_agent_tool_calls:
                return self._decide(
                    actor,
                    action.kind,
                    TrustDecision.DENY,
                    "Tool-call budget exceeded",
                    {"tool_calls": session.tool_calls},
                )

            requested = set(action.requested_capabilities) or {action.kind}
            unknown = requested - ALLOWED_CAPABILITIES
            if unknown and self.settings.deny_by_default:
                return self._decide(
                    actor,
                    action.kind,
                    TrustDecision.DENY,
                    f"Unknown capabilities: {sorted(unknown)}",
                    {"unknown": sorted(unknown)},
                )

            missing = requested - session.granted - ALLOWED_CAPABILITIES
            # Allow known capabilities if session granted them OR they are in the allow list
            # and explicitly requested in a kits4kid workflow open.
            if self.settings.deny_by_default:
                not_granted = requested - session.granted
                # Bootstrap: auto-grant safe draft capabilities
                safe_auto = {"read_scripture", "generate_scene_draft", "storykeeper_draft"}
                auto = not_granted & safe_auto
                session.granted |= auto
                still_missing = requested - session.granted
                if still_missing - PARENT_GATED_ACTIONS:
                    return self._decide(
                        actor,
                        action.kind,
                        TrustDecision.DENY,
                        f"Capabilities not granted: {sorted(still_missing)}",
                        {"missing": sorted(still_missing)},
                    )

            if action.kind in PARENT_GATED_ACTIONS or requested & PARENT_GATED_ACTIONS:
                if self.settings.require_parent_approve and not session.parent_approved:
                    return self._decide(
                        actor,
                        action.kind,
                        TrustDecision.HOLD,
                        "Parent Approve required — draft held in quarantine",
                        {"action_id": action.action_id, "gated": True},
                    )

            return self._decide(
                actor,
                action.kind,
                TrustDecision.ALLOW,
                "Allowed under jail policy",
                {"action_id": action.action_id, "granted": sorted(session.granted)},
            )

    def _decide(
        self,
        actor: str,
        action: str,
        decision: TrustDecision,
        reason: str,
        metadata: dict,
    ) -> PolicyResult:
        event = AuditEvent(
            event_id=new_id("aud_"),
            actor=actor,
            action=action,
            decision=decision,
            reason=reason,
            metadata=metadata,
        )
        self._audit.append(event)
        return PolicyResult(decision=decision, reason=reason, audit=event)

    def recent_audit(self, limit: int = 50) -> list[AuditEvent]:
        with self._lock:
            return list(self._audit[-limit:])


class WasmJail:
    """Placeholder for Wassette / AgentZero WASM sandbox.

    Today: records intended capability envelope.
    Tomorrow: spawn WASM isolate and intercept hostcalls.
    """

    def __init__(self, runtime: str = "wassette-stub") -> None:
        self.runtime = runtime

    def describe(self) -> dict[str, str]:
        return {
            "runtime": self.runtime,
            "status": "stub",
            "enforcement": "policy_engine",
            "upgrade_path": "AgentZero | Wassette | coreason-runtime",
        }


_engine: PolicyEngine | None = None


def get_policy_engine() -> PolicyEngine:
    global _engine
    if _engine is None:
        _engine = PolicyEngine()
    return _engine
