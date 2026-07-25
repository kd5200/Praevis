"""Observability interfaces (metrics/tracing stubs for later backends)."""

from __future__ import annotations

from typing import Protocol


class MetricsClient(Protocol):
    def incr(self, name: str, *, value: int = 1) -> None: ...

    def timing(self, name: str, duration_ms: float) -> None: ...


class NullMetrics:
    """No-op metrics sink used until a backend is configured."""

    def incr(self, name: str, *, value: int = 1) -> None:
        _ = (name, value)

    def timing(self, name: str, duration_ms: float) -> None:
        _ = (name, duration_ms)


metrics: MetricsClient = NullMetrics()
