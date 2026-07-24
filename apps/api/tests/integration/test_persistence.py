"""Persistence helper tests."""

from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from praevis_api.core.config import Settings
from praevis_api.db.models import Scan
from praevis_api.services.scans import create_and_run_scan, get_scan
from praevis_api.storage.artifacts import MemoryArtifactStore

REPO = Path(__file__).resolve().parents[4]
SAFE = (REPO / "tests/fixtures/safe-article.html").read_bytes()
RULES = str(REPO / "packages/security-rules/rules/catalog.json")


def test_persist_scan_roundtrip(db_session: Session) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, content=SAFE)

    settings = Settings(ready_check_dependencies=False, security_rules_path=RULES)
    scan = create_and_run_scan(
        db_session,
        url="https://example.com/persist",
        mode="standard",
        wait_for_completion=True,
        settings=settings,
        artifact_store=MemoryArtifactStore(),
        transport=httpx.MockTransport(handler),
    )
    loaded = get_scan(db_session, scan.id)
    assert loaded is not None
    assert loaded.content is not None
    assert loaded.content.sanitized_text
    assert isinstance(loaded, Scan)
