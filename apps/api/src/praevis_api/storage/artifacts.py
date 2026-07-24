"""Raw artifact storage interface.

Raw page bodies are not stored unrestricted in Postgres. Implementations may
use local disk (MVP), memory (tests), or later encrypted object storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class RawArtifactStore(Protocol):
    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Persist bytes and return an opaque reference string."""

    def get(self, reference: str) -> bytes:
        """Load bytes by reference."""


class MemoryArtifactStore:
    def __init__(self) -> None:
        self._items: dict[str, bytes] = {}

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        _ = content_type
        ref = f"memory://{key}"
        self._items[ref] = data
        return ref

    def get(self, reference: str) -> bytes:
        return self._items[reference]


class LocalArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        _ = content_type
        safe = key.replace("/", "_").replace("..", "_")
        path = self.root / safe
        path.write_bytes(data)
        return f"file://{path.resolve()}"

    def get(self, reference: str) -> bytes:
        if not reference.startswith("file://"):
            raise ValueError("unsupported reference")
        return Path(reference.removeprefix("file://")).read_bytes()


def build_artifact_store(backend: str, path: str) -> RawArtifactStore:
    if backend == "memory":
        return MemoryArtifactStore()
    return LocalArtifactStore(path)
