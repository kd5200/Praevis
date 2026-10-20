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


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/\npayload",
        "https://example.com\r\nX-Injected: true",
        "https://example.com\t/path",
        "\thttps://example.com",
        "https://example.com\n",
        "https://example.com\r@evil.com",
        "http://exa\tmple.com/",
        "fixture://page\n.html",
    ],
)
def test_reject_ascii_control_characters(url: str) -> None:
    with pytest.raises(UrlNormalizationError) as exc:
        normalize_url(url)
    assert exc.value.code == "url_malformed"


def test_whitespace_trim_still_allowed() -> None:
    result = normalize_url("  https://example.com/path  ")
    assert result.scheme == "https"
    assert result.host == "example.com"
    assert result.path == "/path"


def test_fixture_names_still_allowed() -> None:
    result = normalize_url("fixture://direct-prompt-injection.html")
    assert result.scheme == "fixture"
    assert result.normalized == "fixture://direct-prompt-injection.html"
