"""Optional Ray Plasma backend — imported only when TZ_OBJECT_STORE_BACKEND=ray."""

from __future__ import annotations

from app.contracts import ObjectRef, new_id, utcnow
from app.zero_copy.store import StoredObject


class RayPlasmaStore:
    def __init__(self, max_object_bytes: int) -> None:
        import ray

        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
        self._max = max_object_bytes
        self._refs: dict[str, ObjectRef] = {}
        self._ray_ids: dict[str, object] = {}

    def put(
        self,
        data: bytes | memoryview,
        *,
        media_type: str = "application/octet-stream",
        labels: dict[str, str] | None = None,
    ) -> ObjectRef:
        import ray

        raw = bytes(data)
        if len(raw) > self._max:
            raise ValueError(f"Object exceeds max size ({self._max} bytes)")
        object_id = new_id("obj_")
        ray_ref = ray.put(raw)
        ref = ObjectRef(
            object_id=object_id,
            media_type=media_type,
            size_bytes=len(raw),
            created_at=utcnow(),
            labels=labels or {},
        )
        self._refs[object_id] = ref
        self._ray_ids[object_id] = ray_ref
        return ref

    def get(self, object_id: str) -> StoredObject:
        import ray

        if object_id not in self._ray_ids:
            raise KeyError(f"Unknown object_id={object_id}")
        raw = ray.get(self._ray_ids[object_id])
        ref = self._refs[object_id]
        return StoredObject(ref=ref, payload=memoryview(raw), meta=dict(ref.labels))

    def get_ref(self, object_id: str) -> ObjectRef:
        if object_id not in self._refs:
            raise KeyError(f"Unknown object_id={object_id}")
        return self._refs[object_id]

    def exists(self, object_id: str) -> bool:
        return object_id in self._refs
