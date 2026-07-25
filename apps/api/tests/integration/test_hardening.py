"""Hardening: structured errors, rate limits, request id."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from praevis_api.core.config import get_settings
from praevis_api.core.rate_limit import rate_limiter


def test_scan_not_found_structured_error(client: TestClient) -> None:
    missing = uuid.uuid4()
    response = client.get(f"/v1/scans/{missing}")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "scan_not_found"
    assert "request_id" in body["error"]
    assert response.headers.get("X-Request-ID") == body["error"]["request_id"]
    assert "X-Response-Time-Ms" in response.headers


def test_validation_error_structured(client: TestClient) -> None:
    response = client.post("/v1/scans", json={"url": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "request_id" in body["error"]


def test_request_too_large(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "32")
    get_settings.cache_clear()
    # Recreate app would be ideal; Content-Length check uses get_settings at request time.
    response = client.post(
        "/v1/scans",
        content=b'{"url":"https://example.com/' + b"x" * 100 + b'"}',
        headers={"content-type": "application/json", "content-length": "200"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"
    get_settings.cache_clear()


def test_rate_limit_scan_create(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    rate_limiter.reset()
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    get_settings.cache_clear()

    payload = {"url": "http://127.0.0.1/", "wait_for_completion": True}
    first = client.post("/v1/scans", json=payload)
    second = client.post("/v1/scans", json=payload)
    third = client.post("/v1/scans", json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 429
    assert third.json()["error"]["code"] == "rate_limited"
    assert third.headers.get("Retry-After") == "60"

    rate_limiter.reset()
    get_settings.cache_clear()


def test_health_includes_request_id(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-req-1"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-req-1"
