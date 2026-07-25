"""Sanitization / extraction tests."""

from pathlib import Path
from unittest.mock import MagicMock

from bs4 import Tag

from praevis_api.pipeline.extract import _attr_str, _is_hidden, extract_content, sanitize_html

REPO = Path(__file__).resolve().parents[4]


def test_sanitize_removes_script_and_handlers() -> None:
    raw = (REPO / "tests/fixtures/malformed-unsafe.html").read_text(encoding="utf-8")
    cleaned = sanitize_html(raw)
    assert "<script" not in cleaned.lower()
    assert "<iframe" not in cleaned.lower()
    assert "<form" not in cleaned.lower()
    assert "onclick" not in cleaned.lower()
    assert "javascript:" not in cleaned.lower()
    assert "Visible paragraph" in cleaned


def test_sanitize_handles_hidden_and_svg() -> None:
    raw = """
    <html><body>
      <div style="display:none">secret</div>
      <p>Visible</p>
      <svg><g></g></svg>
    </body></html>
    """
    cleaned = sanitize_html(raw)
    assert "secret" not in cleaned.lower()
    assert "Visible" in cleaned


def test_attr_helpers_tolerate_none_attrs() -> None:
    tag = MagicMock(spec=Tag)
    tag.attrs = None
    assert _attr_str(tag, "style") == ""
    assert _is_hidden(tag) is False


def test_extract_safe_article() -> None:
    raw = (REPO / "tests/fixtures/safe-article.html").read_bytes()
    content = extract_content(raw, "text/html")
    assert content.title == "Safe Example Article"
    assert "water cycle" in content.text.lower()
    assert "<script" not in content.html.lower()
