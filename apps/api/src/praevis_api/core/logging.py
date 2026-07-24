"""Structured logging helpers."""

from __future__ import annotations

import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from praevis_api.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure root logging. Avoid logging secrets or full page bodies."""

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
        handler.setFormatter(formatter)
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

    root.addHandler(handler)


def log_extra(
    *,
    request_id: str | None = None,
    scan_id: str | None = None,
    pipeline_stage: str | None = None,
    detector: str | None = None,
    duration_ms: float | None = None,
    outcome: str | None = None,
) -> dict[str, Any]:
    """Build a structured logging extras dict; omit unset fields."""

    payload: dict[str, Any] = {}
    if request_id is not None:
        payload["request_id"] = request_id
    if scan_id is not None:
        payload["scan_id"] = scan_id
    if pipeline_stage is not None:
        payload["pipeline_stage"] = pipeline_stage
    if detector is not None:
        payload["detector"] = detector
    if duration_ms is not None:
        payload["duration_ms"] = duration_ms
    if outcome is not None:
        payload["outcome"] = outcome
    return payload
