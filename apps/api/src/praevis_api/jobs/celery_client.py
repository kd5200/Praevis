"""Celery client used by the API to enqueue scan jobs."""

from __future__ import annotations

from functools import lru_cache

from celery import Celery

from praevis_api.core.config import get_settings

PROCESS_SCAN_TASK = "praevis.worker.process_scan"


@lru_cache
def get_celery_app() -> Celery:
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
        task_always_eager=settings.celery_task_always_eager,
        task_eager_propagates=True,
    )
    return app


def enqueue_process_scan(scan_id: str) -> str:
    """Enqueue asynchronous scan processing. Returns Celery async result id when available."""

    result = get_celery_app().send_task(PROCESS_SCAN_TASK, args=[scan_id])
    return str(result.id)


def reset_celery_app() -> None:
    get_celery_app.cache_clear()
