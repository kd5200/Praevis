"""fixture:// demo URL tests."""

from pathlib import Path

from praevis_api.core.config import Settings
from praevis_api.pipeline.fetch import fetch_resource
from praevis_api.pipeline.normalize import normalize_url
from praevis_api.pipeline.runner import run_scan_pipeline
from praevis_api.storage.artifacts import MemoryArtifactStore

REPO = Path(__file__).resolve().parents[4]
RULES = str(REPO / "packages/security-rules/rules/catalog.json")
ALLOWED = {"text/html", "text/plain"}


def test_normalize_fixture_url() -> None:
    result = normalize_url("fixture://direct-prompt-injection.html")
    assert result.scheme == "fixture"
    assert result.normalized == "fixture://direct-prompt-injection.html"


def test_fetch_fixture() -> None:
    fetched = fetch_resource(
        "fixture://direct-prompt-injection.html",
        max_redirects=1,
        connect_timeout=1,
        read_timeout=1,
        max_bytes=1_000_000,
        user_agent="test",
        allowed_content_types=ALLOWED,
    )
    assert fetched.status_code == 200
    assert b"Ignore previous" in fetched.body


def test_pipeline_fixture_blocks_or_warns() -> None:
    settings = Settings(
        ready_check_dependencies=False,
        security_rules_path=RULES,
        artifact_storage_backend="memory",
    )
    result = run_scan_pipeline(
        "fixture://direct-prompt-injection.html",
        settings=settings,
        artifact_store=MemoryArtifactStore(),
    )
    assert result.findings
    assert result.decision in {"warn", "block"}
    assert result.status in {"completed", "blocked"}
