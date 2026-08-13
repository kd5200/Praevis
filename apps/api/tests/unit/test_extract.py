"""Sanitization / extraction tests."""

from pathlib import Path
from unittest.mock import MagicMock

from bs4 import Tag

from praevis_api.pipeline.extract import (
    _attr_str,
    _is_hidden,
    extract_content,
    sanitize_html,
    sanitize_html_with_transformations,
)

REPO = Path(__file__).resolve().parents[4]


def _targets(transformations: list, type_: str) -> list[str]:
    return [t.target for t in transformations if t.type == type_]


def test_sanitize_removes_script_and_handlers() -> None:
    raw = (REPO / "tests/fixtures/malformed-unsafe.html").read_text(encoding="utf-8")
    cleaned = sanitize_html(raw)
    assert "<script" not in cleaned.lower()
    assert "<iframe" not in cleaned.lower()
    assert "<form" not in cleaned.lower()
    assert "onclick" not in cleaned.lower()
    assert "javascript:" not in cleaned.lower()
    assert "Visible paragraph" in cleaned


def test_sanitize_records_transformations_for_unsafe_html() -> None:
    raw = (REPO / "tests/fixtures/malformed-unsafe.html").read_text(encoding="utf-8")
    _cleaned, transformations = sanitize_html_with_transformations(raw)
    assert transformations
    removed = _targets(transformations, "removed_element")
    assert "script" in removed
    assert "iframe" in removed
    assert "form" in removed
    assert any(t.type == "removed_attribute" and t.target == "onclick" for t in transformations)
    assert any(t.type == "removed_unsafe_url" for t in transformations)


def test_sanitize_handles_hidden_and_svg() -> None:
    raw = """
    <html><body>
      <div style="display:none">secret</div>
      <p>Visible</p>
      <svg><g></g></svg>
    </body></html>
    """
    cleaned, transformations = sanitize_html_with_transformations(raw)
    assert "secret" not in cleaned.lower()
    assert "Visible" in cleaned
    assert any(
        t.type == "removed_element" and t.reason == "hidden_instruction_removal"
        for t in transformations
    )


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
    assert content.transformations == []


def test_extract_plain_text_has_empty_transformations() -> None:
    content = extract_content(b"Hello plain world", "text/plain")
    assert content.text == "Hello plain world"
    assert content.transformations == []
