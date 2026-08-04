"""Context Engineering — retrieval + Zero-Copy packing under a token budget."""

from __future__ import annotations

from app.framework.layers import ContextPack
from app.zero_copy import get_object_store


class ContextEngine:
    def __init__(self) -> None:
        self.store = get_object_store()
        self._memory: dict[str, list[str]] = {}

    def remember(self, session_id: str, text: str) -> None:
        self._memory.setdefault(session_id, []).append(text)
        self._memory[session_id] = self._memory[session_id][-12:]

    def assemble(
        self,
        *,
        session_id: str,
        user_input: str,
        object_ids: list[str] | None = None,
        token_budget: int = 4096,
    ) -> ContextPack:
        snippets: list[str] = []
        resolved_ids: list[str] = []
        for oid in object_ids or []:
            if not self.store.exists(oid):
                continue
            obj = self.store.get(oid)
            resolved_ids.append(oid)
            # Zero-copy: read via memoryview, decode only a preview into context
            preview = bytes(obj.payload[:1200]).decode("utf-8", errors="ignore")
            snippets.append(f"[object:{oid}]\n{preview}")

        mem = self._memory.get(session_id, [])
        packed_parts = []
        if mem:
            packed_parts.append("Session memory:\n" + "\n".join(mem[-4:]))
        if snippets:
            packed_parts.append("Attached evidence:\n" + "\n---\n".join(snippets))
        packed_parts.append(f"User:\n{user_input}")

        packed = "\n\n".join(packed_parts)
        # Soft trim by characters ~ 4 chars/token heuristic
        max_chars = token_budget * 4
        if len(packed) > max_chars:
            packed = packed[-max_chars:]

        return ContextPack(
            object_ids=resolved_ids,
            snippets=snippets,
            memory_keys=[session_id],
            token_budget=token_budget,
            packed_text=packed,
        )
