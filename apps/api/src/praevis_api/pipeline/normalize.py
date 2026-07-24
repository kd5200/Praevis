"""URL normalization stage."""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse, urlunparse

from praevis_api.pipeline.types import NormalizedUrl


class UrlNormalizationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def normalize_url(raw: str) -> NormalizedUrl:
    """Validate and normalize a user-submitted URL.

    - Trim whitespace
    - Require http/https
    - Reject credentials in URL
    - Lowercase scheme/host
    - Drop fragments
    - Normalize path encoding lightly
    """

    if raw is None or not str(raw).strip():
        raise UrlNormalizationError("url_empty", "URL must not be empty")

    candidate = str(raw).strip()
    parsed = urlparse(candidate)

    if not parsed.scheme or not parsed.netloc:
        raise UrlNormalizationError("url_malformed", "URL must include scheme and host")

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise UrlNormalizationError(
            "url_unsupported_scheme", "Only http and https URLs are allowed"
        )

    if parsed.username is not None or parsed.password is not None:
        raise UrlNormalizationError(
            "url_embedded_credentials", "URLs with embedded credentials are not allowed"
        )

    host = parsed.hostname
    if host is None or host == "":
        raise UrlNormalizationError("url_malformed", "URL host is missing")

    host = host.lower().rstrip(".")
    # Reject obviously weird hosts
    if " " in host:
        raise UrlNormalizationError("url_malformed", "URL host is invalid")

    port = parsed.port
    path = parsed.path or "/"
    # Decode then re-encode path segments conservatively
    path = quote(unquote(path), safe="/:@-._~!$&'()*+,;=")
    query = parsed.query
    normalized = urlunparse((scheme, parsed.netloc.lower(), path, "", query, ""))

    return NormalizedUrl(
        original=candidate,
        normalized=normalized,
        scheme=scheme,
        host=host,
        port=port,
        path=path,
    )
