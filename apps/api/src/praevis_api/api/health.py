"""Health and readiness endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response, status

from praevis_api.core.config import Settings, get_settings
from praevis_api.core.deps import check_database, check_redis

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — process is serving requests."""

    settings = get_settings()
    return {"status": "ok", "service": settings.service_name}


@router.get("/ready")
def ready(response: Response) -> dict[str, Any]:
    """Readiness probe — optional dependency checks."""

    settings: Settings = get_settings()
    checks: dict[str, Any] = {}

    if settings.ready_check_dependencies:
        checks["database"] = check_database(settings.database_url)
        checks["redis"] = check_redis(settings.redis_url)
        unhealthy = any(item.get("status") != "ok" for item in checks.values())
        if unhealthy:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not_ready", "service": settings.service_name, "checks": checks}

    return {"status": "ready", "service": settings.service_name, "checks": checks}
