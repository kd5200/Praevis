"""Safe fetcher tests using MockTransport (no public network)."""

from __future__ import annotations

import httpx
import pytest

from praevis_api.pipeline.fetch import FetchError, fetch_resource

ALLOWED = {"text/html", "text/plain"}


def _fetch(handler, url: str, **kwargs):  # type: ignore[no-untyped-def]
    transport = httpx.MockTransport(handler)
    defaults = dict(
        max_redirects=3,
        connect_timeout=1.0,
        read_timeout=1.0,
        max_bytes=1024,
        user_agent="test-agent",
        allowed_content_types=ALLOWED,
        transport=transport,
    )
    defaults.update(kwargs)
    return fetch_resource(url, **defaults)


@pytest.mark.security
def test_fetch_html_ok() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"] == "test-agent"
        return httpx.Response(
            200, headers={"content-type": "text/html"}, content=b"<html><body>ok</body></html>"
        )

    result = _fetch(handler, "https://example.com/page")
    assert result.status_code == 200
    assert result.content_hash.startswith("sha256:")
    assert result.redirect_chain == []


@pytest.mark.security
def test_redirect_loop_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": str(request.url)})

    with pytest.raises(FetchError) as exc:
        _fetch(handler, "https://example.com/loop", max_redirects=2)
    assert exc.value.code == "too_many_redirects"


@pytest.mark.security
def test_public_to_private_redirect_blocked() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "example.com":
            return httpx.Response(302, headers={"location": "http://127.0.0.1/secret"})
        return httpx.Response(200, content=b"nope")

    with pytest.raises(FetchError) as exc:
        _fetch(handler, "https://example.com/start")
    assert exc.value.code == "destination_blocked_ip"


@pytest.mark.security
def test_oversized_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/plain"}, content=b"x" * 2048)

    with pytest.raises(FetchError) as exc:
        _fetch(handler, "https://example.com/big", max_bytes=100)
    assert exc.value.code == "response_too_large"


@pytest.mark.security
def test_unsupported_content_type() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF")

    with pytest.raises(FetchError) as exc:
        _fetch(handler, "https://example.com/doc.pdf")
    assert exc.value.code == "unsupported_content_type"
