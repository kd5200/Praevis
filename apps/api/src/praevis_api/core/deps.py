"""Dependency probe helpers for readiness."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def check_database(database_url: str) -> dict[str, Any]:
    """Return a small status dict for Postgres connectivity."""

    engine: Engine | None = None
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001 — readiness must never raise
        logger.warning("database readiness check failed", extra={"outcome": "failed"})
        return {"status": "error", "detail": type(exc).__name__}
    finally:
        if engine is not None:
            engine.dispose()


def check_redis(redis_url: str) -> dict[str, Any]:
    """Return a small status dict for Redis connectivity."""

    try:
        import redis

        client = redis.Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        try:
            if client.ping():
                return {"status": "ok"}
            return {"status": "error", "detail": "ping_failed"}
        finally:
            client.close()
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis readiness check failed", extra={"outcome": "failed"})
        return {"status": "error", "detail": type(exc).__name__}
