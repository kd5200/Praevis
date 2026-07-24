"""Scan persistence and orchestration service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from praevis_api.core.config import Settings
from praevis_api.db.enums import ScanStatus
from praevis_api.db.models import Finding, RetrievedContent, Scan
from praevis_api.pipeline.runner import run_scan_pipeline
from praevis_api.pipeline.types import PipelineResult
from praevis_api.schemas.scans import (
    ContentOut,
    FindingOut,
    ProvenanceOut,
    ScanOut,
)
from praevis_api.storage.artifacts import RawArtifactStore


def _apply_pipeline_result(scan: Scan, result: PipelineResult, session: Session) -> None:
    scan.status = result.status
    scan.normalized_url = result.normalized_url
    scan.final_url = result.final_url
    scan.overall_risk_score = result.risk_score
    scan.trust_score = result.trust_score
    scan.decision = result.decision
    scan.content_hash = result.content_hash
    scan.redirect_chain = result.redirect_chain
    scan.score_explanation = result.score_explanation
    scan.error_code = result.error_code
    scan.error_message = result.error_message
    scan.completed_at = datetime.now(UTC)

    scan.findings.clear()
    for item in result.findings:
        scan.findings.append(
            Finding(
                category=item.category,
                severity=item.severity,
                detector=item.detector,
                title=item.title,
                description=item.description,
                evidence=item.evidence,
                remediation=item.remediation,
                confidence=item.confidence,
            )
        )

    if result.content is not None:
        if scan.content is None:
            scan.content = RetrievedContent(scan_id=scan.id)
        scan.content.content_type = result.content_type
        scan.content.raw_content_reference = result.raw_content_reference
        scan.content.sanitized_text = result.content.text
        scan.content.sanitized_html = result.content.html
        scan.content.page_title = result.content.title
        scan.content.language = result.content.language
        scan.content.metadata_json = result.content.metadata

    session.add(scan)
    session.commit()
    session.refresh(scan)


def scan_to_schema(scan: Scan, *, include_content: bool = True) -> ScanOut:
    findings = [
        FindingOut(
            id=f.id,
            category=f.category,
            severity=f.severity,
            detector=f.detector,
            title=f.title,
            description=f.description,
            evidence=f.evidence,
            remediation=f.remediation,
            confidence=f.confidence,
        )
        for f in scan.findings
    ]
    content = None
    if include_content and scan.content is not None:
        content = ContentOut(
            title=scan.content.page_title,
            text=scan.content.sanitized_text,
            content_type=scan.content.content_type,
            sanitized_html=scan.content.sanitized_html,
        )
    provenance = ProvenanceOut(
        retrieved_at=scan.completed_at,
        content_hash=scan.content_hash,
        redirect_chain=list(scan.redirect_chain or []),
    )
    return ScanOut(
        scan_id=scan.id,
        status=scan.status,
        submitted_url=scan.submitted_url,
        normalized_url=scan.normalized_url,
        final_url=scan.final_url,
        risk_score=scan.overall_risk_score,
        trust_score=scan.trust_score,
        decision=scan.decision,
        findings=findings,
        content=content,
        provenance=provenance,
        score_explanation=scan.score_explanation,
        error_code=scan.error_code,
        error_message=scan.error_message,
        created_at=scan.created_at,
        completed_at=scan.completed_at,
    )


def create_and_run_scan(
    session: Session,
    *,
    url: str,
    mode: str,
    wait_for_completion: bool,
    settings: Settings,
    artifact_store: RawArtifactStore,
    transport: httpx.BaseTransport | None = None,
) -> Scan:
    scan = Scan(
        submitted_url=url,
        status=ScanStatus.QUEUED.value,
        started_at=datetime.now(UTC),
        request_metadata={"mode": mode, "wait_for_completion": wait_for_completion},
    )
    session.add(scan)
    session.commit()
    session.refresh(scan)

    if not wait_for_completion:
        # Phase 4 will enqueue worker jobs; for now leave queued.
        return scan

    scan.status = ScanStatus.VALIDATING.value
    session.commit()

    result = run_scan_pipeline(
        url,
        settings=settings,
        artifact_store=artifact_store,
        transport=transport,
        request_metadata={"mode": mode},
    )
    _apply_pipeline_result(scan, result, session)
    return scan


def get_scan(session: Session, scan_id: uuid.UUID) -> Scan | None:
    return session.get(Scan, scan_id)


def list_scans(session: Session, *, limit: int = 50, offset: int = 0) -> tuple[list[Scan], int]:
    total = session.scalar(select(func.count()).select_from(Scan)) or 0
    rows = session.scalars(
        select(Scan).order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return list(rows), int(total)
