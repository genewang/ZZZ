"""Zero-Copy object plane.

Production target: Ray Plasma + Apache Arrow shared memory.
Local default: in-process store with Arrow-shaped metadata and zero-copy
memoryview handoff between agents on the same node.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Protocol

from app.config import Settings, get_settings
from app.contracts import ObjectRef, new_id, utcnow


@dataclass
class StoredObject:
    ref: ObjectRef
    payload: memoryview
    meta: dict[str, str] = field(default_factory=dict)


class ObjectStore(Protocol):
    def put(
        self,
        data: bytes | memoryview,
        *,
        media_type: str = "application/octet-stream",
        labels: dict[str, str] | None = None,
    ) -> ObjectRef: ...

    def get(self, object_id: str) -> StoredObject: ...

    def get_ref(self, object_id: str) -> ObjectRef: ...

    def exists(self, object_id: str) -> bool: ...


class MemoryObjectStore:
    """In-memory stand-in for Ray Plasma.

    Returns memoryview slices so co-located workers can read without copying
    the underlying buffer (same process). Swap for Plasma when Ray is enabled.
    """

    def __init__(self, max_object_bytes: int) -> None:
        self._max = max_object_bytes
        self._lock = threading.RLock()
        self._objects: dict[str, StoredObject] = {}

    def put(
        self,
        data: bytes | memoryview,
        *,
        media_type: str = "application/octet-stream",
        labels: dict[str, str] | None = None,
    ) -> ObjectRef:
        raw = bytes(data)
        if len(raw) > self._max:
            raise ValueError(f"Object exceeds max size ({self._max} bytes)")
        object_id = new_id("obj_")
        buf = memoryview(raw)
        ref = ObjectRef(
            object_id=object_id,
            media_type=media_type,
            size_bytes=len(raw),
            created_at=utcnow(),
            labels=labels or {},
        )
        with self._lock:
            self._objects[object_id] = StoredObject(ref=ref, payload=buf, meta=dict(labels or {}))
        return ref

    def get(self, object_id: str) -> StoredObject:
        with self._lock:
            try:
                return self._objects[object_id]
            except KeyError as exc:
                raise KeyError(f"Unknown object_id={object_id}") from exc

    def get_ref(self, object_id: str) -> ObjectRef:
        return self.get(object_id).ref

    def exists(self, object_id: str) -> bool:
        with self._lock:
            return object_id in self._objects


_store: ObjectStore | None = None


def get_object_store(settings: Settings | None = None) -> ObjectStore:
    global _store
    if _store is None:
        cfg = settings or get_settings()
        if cfg.object_store_backend == "ray":
            try:
                from app.zero_copy.ray_store import RayPlasmaStore

                _store = RayPlasmaStore(cfg.max_object_bytes)
            except Exception:
                _store = MemoryObjectStore(cfg.max_object_bytes)
        else:
            _store = MemoryObjectStore(cfg.max_object_bytes)
    return _store
