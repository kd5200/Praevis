"""Celery application skeleton.

Scan jobs are intentionally not implemented in Phase 1.
Pipeline stages will be imported from a shared module in Phase 2/4.
"""

from __future__ import annotations

from celery import Celery

from praevis_worker.config import get_settings

settings = get_settings()

app = Celery(
    "praevis",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@app.task(name="praevis.worker.ping")  # type: ignore[untyped-decorator]
def ping() -> dict[str, str]:
    """Lightweight task used to verify worker wiring."""

    return {"status": "ok", "service": settings.service_name}
