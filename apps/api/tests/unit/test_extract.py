"""Sanitization / extraction tests."""

from pathlib import Path

from praevis_api.pipeline.extract import extract_content, sanitize_html

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


def test_extract_safe_article() -> None:
    raw = (REPO / "tests/fixtures/safe-article.html").read_bytes()
    content = extract_content(raw, "text/html")
    assert content.title == "Safe Example Article"
    assert "water cycle" in content.text.lower()
    assert "<script" not in content.html.lower()
