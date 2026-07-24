"""Cross-cutting security regression tests."""

from pathlib import Path

import httpx
import pytest

from praevis_api.core.config import Settings
from praevis_api.pipeline.runner import run_scan_pipeline
from praevis_api.storage.artifacts import MemoryArtifactStore

REPO = Path(__file__).resolve().parents[2]
RULES = str(REPO / "packages/security-rules/rules/catalog.json")


@pytest.mark.security
def test_end_to_end_hidden_injection_fixture() -> None:
    html = (REPO / "tests/malicious-pages/hidden-prompt-injection.html").read_bytes()

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
