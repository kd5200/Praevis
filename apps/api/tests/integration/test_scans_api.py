"""API scan integration tests with mocked HTTP transport."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[4]
SAFE = (REPO / "tests/fixtures/safe-article.html").read_bytes()
INJECT = (REPO / "tests/malicious-pages/direct-prompt-injection.html").read_bytes()


def _install_transport(client: TestClient, body: bytes, content_type: str = "text/html") -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": content_type}, content=body)

    client.app.state.http_transport = httpx.MockTransport(handler)


def test_create_scan_safe_article(client: TestClient) -> None:
    _install_transport(client, SAFE)
    response = client.post(
        "/v1/scans",
        json={
            "url": "https://example.com/article",
            "mode": "standard",
            "wait_for_completion": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] in {"completed", "blocked"}
    assert data["submitted_url"] == "https://example.com/article"
    assert data["content"]["title"] == "Safe Example Article"
    assert data["provenance"]["content_hash"].startswith("sha256:")
    assert data["provenance"]["original_content_hash"] == data["provenance"]["content_hash"]
    assert data["provenance"]["sanitized_content_hash"].startswith("sha256:")
    assert data["integrity"]["original_content_hash"] == data["provenance"]["content_hash"]
    assert data["integrity"]["sanitized_content_hash"] == data["provenance"]["sanitized_content_hash"]
    assert data["integrity"]["original_content_hash"] != data["integrity"]["sanitized_content_hash"]
    assert data["decision"] in {"allow", "warn", "block"}
    scan_id = data["scan_id"]

    detail = client.get(f"/v1/scans/{scan_id}")
    assert detail.status_code == 200
    findings = client.get(f"/v1/scans/{scan_id}/findings")
    assert findings.status_code == 200
    content = client.get(f"/v1/scans/{scan_id}/content")
    assert content.status_code == 200
    listing = client.get("/v1/scans")
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1


@pytest.mark.security
def test_create_scan_prompt_injection_blocks_or_warns(client: TestClient) -> None:
    _install_transport(client, INJECT)
    response = client.post(
        "/v1/scans",
        json={"url": "https://example.com/inject", "wait_for_completion": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["findings"]
    assert data["decision"] in {"warn", "block"}
    assert data["risk_score"] is not None and data["risk_score"] > 0


@pytest.mark.security
def test_blocked_localhost_url(client: TestClient) -> None:
    response = client.post(
        "/v1/scans",
        json={"url": "http://127.0.0.1/", "wait_for_completion": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] in {"blocked", "failed"}
    assert data["decision"] == "block"
    assert data["error_code"] in {
        "destination_blocked_ip",
        "destination_blocked_host",
        "url_malformed",
    }


def test_async_mode_enqueues_and_stays_queued(client: TestClient) -> None:
    response = client.post(
        "/v1/scans",
        json={"url": "https://example.com/later", "wait_for_completion": False},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "queued"
    detail = client.get(f"/v1/scans/{data['scan_id']}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "queued"


def test_async_eager_processes_inline(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from praevis_api.core.config import get_settings

    monkeypatch.setenv("CELERY_TASK_ALWAYS_EAGER", "true")
    get_settings.cache_clear()
    _install_transport(client, SAFE)
    response = client.post(
        "/v1/scans",
        json={"url": "https://example.com/eager", "wait_for_completion": False},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] in {"completed", "blocked"}
    assert data["content"] is not None
    get_settings.cache_clear()
