"""Prompt-injection detector unit tests."""

from pathlib import Path

import pytest

from praevis_api.pipeline.detect import run_security_detectors

REPO = Path(__file__).resolve().parents[4]
RULES = str(REPO / "packages/security-rules/rules/catalog.json")
MAL = REPO / "tests/malicious-pages"


@pytest.mark.security
def test_direct_prompt_injection_detected() -> None:
    html = (MAL / "direct-prompt-injection.html").read_text(encoding="utf-8")
    findings = run_security_detectors(text=html, raw_html=html, rules_path=RULES)
    detectors = {f.detector for f in findings}
    assert "pi-ignore-previous" in detectors
    assert any(f.evidence for f in findings)


@pytest.mark.security
def test_hidden_prompt_injection_detected() -> None:
    html = (MAL / "hidden-prompt-injection.html").read_text(encoding="utf-8")
    # Visible text alone should not include the ignore instruction
    from praevis_api.pipeline.extract import extract_content

    extracted = extract_content(html.encode(), "text/html")
    findings = run_security_detectors(text=extracted.text, raw_html=html, rules_path=RULES)
    assert findings
    assert any("hidden" in f.title.lower() or f.detector.startswith("pi-") for f in findings)
