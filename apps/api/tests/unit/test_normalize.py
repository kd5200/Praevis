"""URL normalization unit tests."""

import pytest

from praevis_api.pipeline.normalize import UrlNormalizationError, normalize_url


def test_normalize_basic_https() -> None:
    result = normalize_url("  HTTPS://Example.COM/Path/../a  ")
    assert result.scheme == "https"
    assert result.host == "example.com"
    assert result.normalized.startswith("https://example.com/")


def test_reject_ftp() -> None:
    with pytest.raises(UrlNormalizationError) as exc:
        normalize_url("ftp://example.com/file")
    assert exc.value.code == "url_unsupported_scheme"


def test_reject_credentials() -> None:
    with pytest.raises(UrlNormalizationError) as exc:
        normalize_url("https://user:pass@example.com/")
    assert exc.value.code == "url_embedded_credentials"


def test_reject_empty() -> None:
    with pytest.raises(UrlNormalizationError) as exc:
        normalize_url("   ")
    assert exc.value.code == "url_empty"
