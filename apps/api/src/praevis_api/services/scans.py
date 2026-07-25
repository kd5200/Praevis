"""Scan persistence and orchestration service."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from praevis_api.core.config import Settings
from praevis_api.core.logging import log_extra
from praevis_api.db.enums import ScanStatus
from praevis_api.db.models import Finding, RetrievedContent, Scan
from praevis_api.jobs.celery_client import enqueue_process_scan
from praevis_api.pipeline.runner import run_scan_pipeline
from praevis_api.pipeline.types import PipelineResult
from praevis_api.schemas.scans import (
    ContentOut,
    FindingOut,
    IntegrityOut,
    ProvenanceOut,
    ScanOut,
)
from praevis_api.storage.artifacts import RawArtifactStore, build_artifact_store

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {
    ScanStatus.COMPLETED.value,
    ScanStatus.BLOCKED.value,
    ScanStatus.FAILED.value,
}


def _apply_pipeline_result(scan: Scan, result: PipelineResult, session: Session) -> None:
    scan.status = result.status
    scan.normalized_url = result.normalized_url
    scan.final_url = result.final_url
    scan.overall_risk_score = result.risk_score
    scan.trust_score = result.trust_score
    scan.decision = result.decision
    scan.content_hash = result.content_hash
    scan.sanitized_content_hash = result.sanitized_content_hash
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
        original_content_hash=scan.content_hash,
        sanitized_content_hash=scan.sanitized_content_hash,
        redirect_chain=list(scan.redirect_chain or []),
        requested_url=scan.submitted_url,
        normalized_url=scan.normalized_url,
        final_url=scan.final_url,
    )
    integrity = IntegrityOut(
        original_content_hash=scan.content_hash,
        sanitized_content_hash=scan.sanitized_content_hash,
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
        integrity=integrity,
        score_explanation=scan.score_explanation,
        error_code=scan.error_code,
        error_message=scan.error_message,
        created_at=scan.created_at,
        completed_at=scan.completed_at,
    )


def process_existing_scan(
    session: Session,
    scan_id: uuid.UUID,
    *,
    settings: Settings,
    artifact_store: RawArtifactStore | None = None,
    transport: httpx.BaseTransport | None = None,
) -> Scan:
    """Run the pipeline for an existing scan row (sync or worker)."""

    scan = session.get(Scan, scan_id)
    if scan is None:
        raise ValueError(f"scan_not_found:{scan_id}")

    if scan.status in TERMINAL_STATUSES:
        return scan

    store = artifact_store or build_artifact_store(
        settings.artifact_storage_backend,
        settings.artifact_storage_path,
    )
    mode = "standard"
    if isinstance(scan.request_metadata, dict):
        mode = str(scan.request_metadata.get("mode") or "standard")

    scan.status = ScanStatus.VALIDATING.value
    if scan.started_at is None:
        scan.started_at = datetime.now(UTC)
    session.commit()

    logger.info(
        "processing scan",
        extra=log_extra(
            scan_id=str(scan.id), pipeline_stage="validate_destination", outcome="started"
        ),
    )

    try:
        result = run_scan_pipeline(
            scan.submitted_url,
            settings=settings,
            artifact_store=store,
            transport=transport,
            request_metadata={"mode": mode},
        )
    except Exception as exc:  # noqa: BLE001 — never leave scans stuck mid-pipeline
        logger.exception(
            "scan pipeline crashed",
            extra=log_extra(scan_id=str(scan.id), pipeline_stage="pipeline", outcome="error"),
        )
        scan.status = ScanStatus.FAILED.value
        scan.error_code = "pipeline_error"
        scan.error_message = f"{type(exc).__name__}: {exc}"[:500]
        scan.completed_at = datetime.now(UTC)
        session.add(scan)
        session.commit()
        session.refresh(scan)
        return scan

    _apply_pipeline_result(scan, result, session)
    logger.info(
        "scan processed",
        extra=log_extra(
            scan_id=str(scan.id), pipeline_stage="finalize_decision", outcome=result.decision
        ),
    )
    return scan


def create_and_run_scan(
    session: Session,
    *,
    url: str,
    mode: str,
    wait_for_completion: bool,
    settings: Settings,
    artifact_store: RawArtifactStore,
    transport: httpx.BaseTransport | None = None,
    enqueue: bool = True,
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

    if wait_for_completion:
        return process_existing_scan(
            session,
            scan.id,
            settings=settings,
            artifact_store=artifact_store,
            transport=transport,
        )

    if enqueue:
        if settings.celery_task_always_eager:
            # Local/test helper: run pipeline inline without a worker process.
            return process_existing_scan(
                session,
                scan.id,
                settings=settings,
                artifact_store=artifact_store,
                transport=transport,
            )
        try:
            task_id = enqueue_process_scan(str(scan.id))
            meta = dict(scan.request_metadata or {})
            meta["celery_task_id"] = task_id
            scan.request_metadata = meta
            session.add(scan)
            session.commit()
            session.refresh(scan)
        except Exception:  # noqa: BLE001 — leave queued; operator can retry/requeue
            logger.exception(
                "failed to enqueue scan",
                extra=log_extra(scan_id=str(scan.id), outcome="enqueue_failed"),
            )
    return scan


def get_scan(session: Session, scan_id: uuid.UUID) -> Scan | None:
    return session.get(Scan, scan_id)


def list_scans(session: Session, *, limit: int = 50, offset: int = 0) -> tuple[list[Scan], int]:
    total = session.scalar(select(func.count()).select_from(Scan)) or 0
    rows = session.scalars(
        select(Scan).order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return list(rows), int(total)
