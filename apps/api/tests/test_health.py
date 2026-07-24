"""API health endpoint tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from praevis_api.core.config import get_settings
from praevis_api.main import create_app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("READY_CHECK_DEPENDENCIES", "false")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "praevis-api"


def test_ready_without_dependency_checks(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["service"] == "praevis-api"
