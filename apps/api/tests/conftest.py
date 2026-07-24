"""Shared pytest fixtures for API and pipeline tests."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from praevis_api.core.config import get_settings
from praevis_api.db.base import Base
from praevis_api.db.session import get_db, reset_engine
from praevis_api.main import create_app
from praevis_api.storage.artifacts import MemoryArtifactStore

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / "packages/security-rules/rules/catalog.json"
FIXTURES = REPO_ROOT / "tests/fixtures"
MALICIOUS = REPO_ROOT / "tests/malicious-pages"


@pytest.fixture()
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture()
def rules_path() -> str:
    return str(RULES_PATH)


@pytest.fixture()
def memory_store() -> MemoryArtifactStore:
    return MemoryArtifactStore()


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


@pytest.fixture()
def client(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("READY_CHECK_DEPENDENCIES", "false")
    monkeypatch.setenv("ARTIFACT_STORAGE_BACKEND", "memory")
    monkeypatch.setenv("SECURITY_RULES_PATH", str(RULES_PATH))
    get_settings.cache_clear()
    reset_engine()

    app = create_app()

    def _override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    reset_engine()
