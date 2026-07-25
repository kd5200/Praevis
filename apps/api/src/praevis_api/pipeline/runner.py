"""Orchestrate scan pipeline stages (framework-independent)."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

import httpx

from praevis_api.core.config import Settings
from praevis_api.core.logging import log_extra
from praevis_api.db.enums import ScanStatus
from praevis_api.pipeline.detect import run_security_detectors
from praevis_api.pipeline.extract import extract_content
from praevis_api.pipeline.fetch import FetchError, fetch_resource
from praevis_api.pipeline.integrity import sha256_digest
from praevis_api.pipeline.normalize import UrlNormalizationError, normalize_url
from praevis_api.pipeline.score import calculate_scores
from praevis_api.pipeline.types import PipelineFinding, PipelineResult
from praevis_api.pipeline.validate_destination import DestinationValidationError
from praevis_api.storage.artifacts import RawArtifactStore

logger = logging.getLogger(__name__)


def _allowed_types(settings: Settings) -> set[str]:
    return {
        part.strip().lower()
        for part in settings.http_allowed_content_types.split(",")
        if part.strip()
    }


def _resolve_rules_path(settings: Settings) -> str:
    path = Path(settings.security_rules_path)
    if path.is_file():
        return str(path)
    # Resolve relative to repo root from common cwd locations
    for base in (Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent):
        candidate = base / settings.security_rules_path
        if candidate.is_file():
            return str(candidate)
        candidate = base / "packages/security-rules/rules/catalog.json"
        if candidate.is_file():
            return str(candidate)
    return settings.security_rules_path


def run_scan_pipeline(
    submitted_url: str,
    *,
    settings: Settings,
    artifact_store: RawArtifactStore,
    transport: httpx.BaseTransport | None = None,
    request_metadata: dict[str, Any] | None = None,
) -> PipelineResult:
    """Run the full scan pipeline synchronously."""

    _ = request_metadata
    findings: list[PipelineFinding] = []
    started = perf_counter()
    scan_token = str(uuid4())

    try:
        stage = "normalize_url"
        t0 = perf_counter()
        normalized = normalize_url(submitted_url)
        logger.info(
            "pipeline stage complete",
            extra=log_extra(
                scan_id=scan_token,
                pipeline_stage=stage,
                duration_ms=(perf_counter() - t0) * 1000,
                outcome="ok",
            ),
        )

        stage = "validate_destination"
        # Full DNS validation occurs inside fetch when transport is None.
        normalize_host_check = normalize_url(normalized.normalized)
        _ = normalize_host_check

        stage = "fetch_resource"
        t0 = perf_counter()
        fetched = fetch_resource(
            normalized.normalized,
            max_redirects=settings.http_max_redirects,
            connect_timeout=settings.http_timeout_connect_seconds,
            read_timeout=settings.http_timeout_read_seconds,
            max_bytes=settings.http_max_response_bytes,
            user_agent=settings.http_user_agent,
            allowed_content_types=_allowed_types(settings),
            transport=transport,
        )
        logger.info(
            "pipeline stage complete",
            extra=log_extra(
                scan_id=scan_token,
                pipeline_stage=stage,
                duration_ms=(perf_counter() - t0) * 1000,
                outcome="ok",
            ),
        )

        stage = "persist_raw_artifact"
        raw_ref = artifact_store.put(
            f"{scan_token}.raw",
            fetched.body,
            content_type=fetched.content_type,
        )

        stage = "extract_content"
        extracted = extract_content(fetched.body, fetched.content_type)
        sanitized_content_hash = sha256_digest(extracted.text)

        stage = "run_security_detectors"
        rules_path = _resolve_rules_path(settings)
        raw_html = (
            fetched.body.decode("utf-8", errors="replace")
            if "html" in fetched.content_type
            else None
        )
        findings.extend(
            run_security_detectors(text=extracted.text, raw_html=raw_html, rules_path=rules_path)
        )

        stage = "calculate_scores"
        scores = calculate_scores(
            findings,
            is_https=fetched.final_url.startswith("https://"),
            redirect_count=len(fetched.redirect_chain),
            block_threshold=settings.risk_block_threshold,
            warn_threshold=settings.risk_warn_threshold,
        )

        status = (
            ScanStatus.BLOCKED.value if scores.decision == "block" else ScanStatus.COMPLETED.value
        )

        logger.info(
            "pipeline complete",
            extra=log_extra(
                scan_id=scan_token,
                pipeline_stage="finalize_decision",
                duration_ms=(perf_counter() - started) * 1000,
                outcome=scores.decision,
            ),
        )

        return PipelineResult(
            status=status,
            submitted_url=submitted_url,
            normalized_url=normalized.normalized,
            final_url=fetched.final_url,
            risk_score=scores.risk_score,
            trust_score=scores.trust_score,
            decision=scores.decision,
            findings=findings,
            content=extracted,
            content_hash=fetched.content_hash,
            redirect_chain=fetched.redirect_chain,
            raw_content_reference=raw_ref,
            content_type=fetched.content_type,
            score_explanation=scores.explanation,
            retrieved_at=fetched.retrieved_at,
            sanitized_content_hash=sanitized_content_hash,
        )
    except (UrlNormalizationError, DestinationValidationError, FetchError) as exc:
        logger.warning(
            "pipeline blocked/failed",
            extra=log_extra(
                scan_id=scan_token,
                pipeline_stage=stage,
                duration_ms=(perf_counter() - started) * 1000,
                outcome="failed",
            ),
        )
        code = getattr(exc, "code", "pipeline_error")
        message = getattr(exc, "message", str(exc))
        # Destination / SSRF style failures are blocked decisions
        blocked_codes = {
            "destination_blocked_ip",
            "destination_blocked_host",
            "url_embedded_credentials",
            "url_unsupported_scheme",
            "too_many_redirects",
        }
        status = ScanStatus.BLOCKED.value if code in blocked_codes else ScanStatus.FAILED.value
        decision = "block" if status == ScanStatus.BLOCKED.value else None
        findings.append(
            PipelineFinding(
                category="ssrf" if "destination" in code or code.startswith("url_") else "policy",
                severity="high",
                detector=f"pipeline:{code}",
                title="Scan blocked by security policy" if decision == "block" else "Scan failed",
                description=message,
                evidence=submitted_url,
                remediation="Submit a public http(s) URL that does not target private networks.",
                confidence=1.0,
            )
        )
        scores = calculate_scores(
            findings,
            is_https=submitted_url.lower().startswith("https://"),
            redirect_count=0,
            block_threshold=settings.risk_block_threshold,
            warn_threshold=settings.risk_warn_threshold,
        )
        return PipelineResult(
            status=status,
            submitted_url=submitted_url,
            normalized_url=None,
            final_url=None,
            risk_score=scores.risk_score,
            trust_score=scores.trust_score,
            decision=decision or scores.decision,
            findings=findings,
            content=None,
            content_hash=None,
            redirect_chain=[],
            raw_content_reference=None,
            content_type=None,
            score_explanation=scores.explanation,
            error_code=code,
            error_message=message,
            sanitized_content_hash=None,
        )
