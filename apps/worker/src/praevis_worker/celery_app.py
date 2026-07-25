"""Celery application and scan processing tasks.

The scan pipeline lives in `praevis_api` and is invoked here so the same stages
run in-process (API sync mode) or in the worker (async mode).
"""

from __future__ import annotations

import logging
import uuid

from celery import Celery

from praevis_worker.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

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
    imports=("praevis_worker.celery_app",),
)


@app.task(name="praevis.worker.ping")  # type: ignore[untyped-decorator]
def ping() -> dict[str, str]:
    """Lightweight task used to verify worker wiring."""

    return {"status": "ok", "service": settings.service_name}


@app.task(name="praevis.worker.process_scan", bind=True, max_retries=2)  # type: ignore[untyped-decorator]
def process_scan(self, scan_id: str) -> dict[str, str]:  # type: ignore[no-untyped-def]
    """Process a queued scan using the shared API pipeline."""

    # Late imports keep Celery worker startup resilient if API package is missing in some envs.
    from praevis_api.core.config import get_settings as get_api_settings
    from praevis_api.db.session import get_session_factory, reset_engine
    from praevis_api.services.scans import process_existing_scan

    # Ensure worker process picks up DATABASE_URL from environment / shared settings.
    reset_engine()
    api_settings = get_api_settings()
    session = get_session_factory()()
    try:
        scan = process_existing_scan(
            session,
            uuid.UUID(scan_id),
            settings=api_settings,
        )
        return {
            "status": scan.status,
            "scan_id": str(scan.id),
            "decision": scan.decision or "",
        }
    except ValueError:
        logger.exception("process_scan rejected for %s", scan_id)
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("process_scan failed for %s", scan_id)
        raise self.retry(exc=exc, countdown=2) from exc
    finally:
        session.close()
