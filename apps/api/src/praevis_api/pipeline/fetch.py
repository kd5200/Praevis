"""Safe HTTP fetcher with manual redirect handling and SSRF revalidation."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urljoin, urlparse

import httpx

from praevis_api.pipeline.normalize import UrlNormalizationError, normalize_url
from praevis_api.pipeline.types import FetchResult
from praevis_api.pipeline.validate_destination import (
    DestinationValidationError,
    validate_destination_url,
)

TransportFactory = Callable[[], httpx.BaseTransport | None]


class FetchError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _content_type_allowed(content_type: str, allowlist: set[str]) -> bool:
    media = content_type.split(";")[0].strip().lower()
    return media in allowlist


def fetch_resource(
    url: str,
    *,
    max_redirects: int,
    connect_timeout: float,
    read_timeout: float,
    max_bytes: int,
    user_agent: str,
    allowed_content_types: set[str],
    transport: httpx.BaseTransport | None = None,
) -> FetchResult:
    """Fetch URL with SSRF-safe redirect following. Does not execute JavaScript."""

    current = normalize_url(url).normalized
    redirect_chain: list[str] = []
    timeout = httpx.Timeout(connect_timeout, read=read_timeout)
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
    }

    with httpx.Client(
        timeout=timeout,
        follow_redirects=False,
        headers=headers,
        transport=transport,
    ) as client:
        for _ in range(max_redirects + 1):
            try:
                validate_destination_url(current, resolve_dns=transport is None)
            except (DestinationValidationError, UrlNormalizationError) as exc:
                code = getattr(exc, "code", "destination_blocked")
                raise FetchError(code, str(exc)) from exc

            try:
                # Stream to enforce size limits without buffering unlimited bodies.
                with client.stream("GET", current) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise FetchError(
                                "redirect_missing_location", "Redirect response missing Location"
                            )
                        next_url = urljoin(current, location)
                        try:
                            next_norm = normalize_url(next_url).normalized
                        except UrlNormalizationError as exc:
                            raise FetchError(exc.code, exc.message) from exc
                        # Revalidate redirect target (public→private blocked via IP checks)
                        try:
                            validate_destination_url(next_norm, resolve_dns=transport is None)
                        except DestinationValidationError as exc:
                            raise FetchError(exc.code, exc.message) from exc
                        redirect_chain.append(next_norm)
                        current = next_norm
                        continue

                    content_type = response.headers.get("content-type", "application/octet-stream")
                    if not _content_type_allowed(content_type, allowed_content_types):
                        raise FetchError(
                            "unsupported_content_type",
                            f"Content type {content_type!r} is not allowed",
                        )

                    chunks: list[bytes] = []
                    total = 0
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > max_bytes:
                            raise FetchError("response_too_large", "Response exceeds size limit")
                        chunks.append(chunk)
                    body = b"".join(chunks)
                    response.raise_for_status()
                    digest = hashlib.sha256(body).hexdigest()
                    return FetchResult(
                        final_url=str(response.url) if response.url else current,
                        status_code=response.status_code,
                        content_type=content_type.split(";")[0].strip().lower(),
                        body=body,
                        redirect_chain=redirect_chain,
                        retrieved_at=datetime.now(UTC),
                        content_hash=f"sha256:{digest}",
                    )
            except httpx.TimeoutException as exc:
                raise FetchError("fetch_timeout", "Upstream request timed out") from exc
            except httpx.HTTPStatusError as exc:
                raise FetchError(
                    "fetch_http_error", f"Upstream returned HTTP {exc.response.status_code}"
                ) from exc
            except httpx.HTTPError as exc:
                raise FetchError(
                    "fetch_failed", f"Upstream request failed: {type(exc).__name__}"
                ) from exc

        raise FetchError("too_many_redirects", f"Exceeded redirect limit of {max_redirects}")


def is_public_to_private_redirect(chain: list[str], final_blocked: bool) -> bool:
    """Helper for tests/docs — redirects into blocked space are rejected during fetch."""

    _ = chain
    return final_blocked


def host_of(url: str) -> str | None:
    return urlparse(url).hostname
