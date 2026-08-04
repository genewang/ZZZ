"""Flywheel Engineering — action traces, labelling signals, compile candidates."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from app.contracts import new_id
from app.framework.layers import FlywheelEvent
from app.zero_token.router import COMPILED_WORKFLOWS


@dataclass
class FlywheelStats:
    events: int = 0
    corrections: int = 0
    compile_candidates: int = 0


class FlywheelEngine:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._events: list[FlywheelEvent] = []
        self._prompt_counts: dict[str, int] = {}
        self.stats = FlywheelStats()

    def record(self, event: FlywheelEvent) -> str:
        event_id = new_id("fw_")
        with self._lock:
            self._events.append(event)
            self.stats.events += 1
            if event.corrections:
                self.stats.corrections += 1
            key = event.prompt.strip().lower()[:160]
            self._prompt_counts[key] = self._prompt_counts.get(key, 0) + 1
            if self._prompt_counts[key] >= 3 and key not in COMPILED_WORKFLOWS:
                self.stats.compile_candidates += 1
        return event_id

    def recent(self, limit: int = 50) -> list[FlywheelEvent]:
        with self._lock:
            return list(self._events[-limit:])

    def compile_candidates(self, min_count: int = 3) -> list[dict[str, str | int]]:
        with self._lock:
            return [
                {"prompt": k, "count": v}
                for k, v in sorted(self._prompt_counts.items(), key=lambda kv: -kv[1])
                if v >= min_count
            ]
