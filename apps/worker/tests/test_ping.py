"""Worker task unit tests (no Redis required)."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from praevis_api.core.config import Settings
from praevis_api.db.base import Base
from praevis_api.db.enums import ScanStatus
from praevis_api.services.scans import create_and_run_scan, process_existing_scan
from praevis_api.storage.artifacts import MemoryArtifactStore
from praevis_worker import __version__
from praevis_worker.celery_app import ping

REPO = Path(__file__).resolve().parents[3]
SAFE = (REPO / "tests/fixtures/safe-article.html").read_bytes()
RULES = str(REPO / "packages/security-rules/rules/catalog.json")


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_package_version() -> None:
    assert __version__ == "0.1.0"


def test_ping_task_body() -> None:
    result = ping()
    assert result["status"] == "ok"
    assert result["service"] == "praevis-worker"


def test_process_existing_scan_from_queued(db_session: Session) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, content=SAFE)

    settings = Settings(
        ready_check_dependencies=False,
        security_rules_path=RULES,
        artifact_storage_backend="memory",
    )
    scan = create_and_run_scan(
        db_session,
        url="https://example.com/queued",
        mode="standard",
        wait_for_completion=False,
        settings=settings,
        artifact_store=MemoryArtifactStore(),
        enqueue=False,
    )
    assert scan.status == ScanStatus.QUEUED.value

    processed = process_existing_scan(
        db_session,
        scan.id,
        settings=settings,
        artifact_store=MemoryArtifactStore(),
        transport=httpx.MockTransport(handler),
    )
    assert processed.status in {ScanStatus.COMPLETED.value, ScanStatus.BLOCKED.value}
    assert processed.content is not None
