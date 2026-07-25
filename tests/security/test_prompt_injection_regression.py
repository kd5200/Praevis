"""Security regression tests across malicious fixtures."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from praevis_api.core.config import Settings
from praevis_api.pipeline.detect import run_security_detectors
from praevis_api.pipeline.extract import extract_content
from praevis_api.pipeline.runner import run_scan_pipeline
from praevis_api.storage.artifacts import MemoryArtifactStore

REPO = Path(__file__).resolve().parents[2]
RULES = str(REPO / "packages/security-rules/rules/catalog.json")
MAL = REPO / "tests/malicious-pages"


@pytest.mark.security
@pytest.mark.parametrize(
    ("filename", "expected_detectors"),
    [
        ("direct-prompt-injection.html", {"pi-ignore-previous"}),
        ("hidden-prompt-injection.html", {"pi-ignore-previous", "pi-hidden-suspicious"}),
        ("tool-manipulation.html", {"pi-tool-manipulation"}),
        ("encoded-instructions.html", {"pi-encoded-instructions"}),
        ("role-markers.html", {"pi-assistant-role"}),
        ("zero-width-injection.html", {"pi-ignore-previous", "pi-reveal-secrets"}),
        ("command-execution.html", {"pi-execute-commands"}),
    ],
)
def test_malicious_fixture_detectors(filename: str, expected_detectors: set[str]) -> None:
    html = (MAL / filename).read_text(encoding="utf-8")
    extracted = extract_content(html.encode("utf-8"), "text/html")
    findings = run_security_detectors(
        text=extracted.text,
        raw_html=html,
        rules_path=RULES,
    )
    detectors = {f.detector for f in findings}
    assert expected_detectors & detectors, (
        f"{filename}: expected one of {expected_detectors}, got {detectors}"
    )


@pytest.mark.security
def test_end_to_end_hidden_injection_fixture() -> None:
    html = (MAL / "hidden-prompt-injection.html").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, content=html)

    settings = Settings(
        ready_check_dependencies=False,
        security_rules_path=RULES,
        artifact_storage_backend="memory",
    )
    result = run_scan_pipeline(
        "https://example.com/hidden",
        settings=settings,
        artifact_store=MemoryArtifactStore(),
        transport=httpx.MockTransport(handler),
    )
    assert result.findings
    assert result.decision in {"warn", "block"}
    assert result.content is not None
    assert "Ignore previous" not in (result.content.text or "")


@pytest.mark.security
def test_pipeline_blocks_metadata_host() -> None:
    settings = Settings(
        ready_check_dependencies=False,
        security_rules_path=RULES,
        artifact_storage_backend="memory",
    )
    result = run_scan_pipeline(
        "http://metadata.google.internal/latest/meta-data/",
        settings=settings,
        artifact_store=MemoryArtifactStore(),
        transport=httpx.MockTransport(lambda r: httpx.Response(200, content=b"nope")),
    )
    assert result.status in {"blocked", "failed"}
    assert result.decision == "block"
    assert result.error_code in {
        "destination_blocked_host",
        "destination_blocked_ip",
        "url_malformed",
    }
