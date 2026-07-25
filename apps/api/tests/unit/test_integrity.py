"""Integrity hash helpers and pipeline hash coverage."""

from pathlib import Path

from praevis_api.pipeline.extract import extract_content
from praevis_api.pipeline.integrity import sha256_digest

REPO = Path(__file__).resolve().parents[4]


def test_sha256_digest_stable_for_text() -> None:
    assert sha256_digest("hello") == sha256_digest(b"hello")
    assert sha256_digest("hello").startswith("sha256:")
    assert sha256_digest("hello") != sha256_digest("hello!")


def test_sanitized_hash_differs_from_raw_when_scripts_removed() -> None:
    raw = (REPO / "tests/fixtures/malformed-unsafe.html").read_bytes()
    extracted = extract_content(raw, "text/html")
    original = sha256_digest(raw)
    sanitized = sha256_digest(extracted.text)
    assert original.startswith("sha256:")
    assert sanitized.startswith("sha256:")
    assert original != sanitized
    assert "<script" not in extracted.text.lower()
