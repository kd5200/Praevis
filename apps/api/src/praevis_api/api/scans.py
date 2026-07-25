"""Scan API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from praevis_api.core.config import Settings, get_settings
from praevis_api.core.errors import (
    CONTENT_NOT_FOUND,
    SCAN_NOT_FOUND,
    VALIDATION_ERROR,
    AppError,
)
from praevis_api.db.session import get_db
from praevis_api.observability.metrics import metrics
from praevis_api.schemas.scans import FindingOut, ScanCreateRequest, ScanListOut, ScanOut
from praevis_api.services import scans as scan_service
from praevis_api.storage.artifacts import RawArtifactStore, build_artifact_store

router = APIRouter(prefix="/v1/scans", tags=["scans"])


def get_artifact_store(settings: Annotated[Settings, Depends(get_settings)]) -> RawArtifactStore:
    return build_artifact_store(settings.artifact_storage_backend, settings.artifact_storage_path)


def get_http_transport(request: Request) -> httpx.BaseTransport | None:
    return getattr(request.app.state, "http_transport", None)


@router.post("", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def create_scan(
    body: ScanCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    artifact_store: Annotated[RawArtifactStore, Depends(get_artifact_store)],
    transport: Annotated[httpx.BaseTransport | None, Depends(get_http_transport)],
) -> ScanOut:
    if len(body.url) > settings.max_url_length:
        raise AppError(
            code=VALIDATION_ERROR,
            message=f"URL exceeds max length of {settings.max_url_length}",
            status_code=422,
        )
    metrics.incr("scans_created")
    scan = scan_service.create_and_run_scan(
        db,
        url=body.url,
        mode=body.mode,
        wait_for_completion=body.wait_for_completion,
        settings=settings,
        artifact_store=artifact_store,
        transport=transport,
    )
    return scan_service.scan_to_schema(scan)


@router.get("", response_model=ScanListOut)
def list_scans(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ScanListOut:
    rows, total = scan_service.list_scans(db, limit=limit, offset=offset)
    return ScanListOut(
        items=[scan_service.scan_to_schema(s, include_content=False) for s in rows], total=total
    )


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> ScanOut:
    scan = scan_service.get_scan(db, scan_id)
    if scan is None:
        raise AppError(code=SCAN_NOT_FOUND, message="Scan not found", status_code=404)
    return scan_service.scan_to_schema(scan)


@router.get("/{scan_id}/findings", response_model=list[FindingOut])
def get_findings(scan_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> list[FindingOut]:
    scan = scan_service.get_scan(db, scan_id)
    if scan is None:
        raise AppError(code=SCAN_NOT_FOUND, message="Scan not found", status_code=404)
    return scan_service.scan_to_schema(scan).findings


@router.get("/{scan_id}/content")
def get_content(scan_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> dict[str, object]:
    scan = scan_service.get_scan(db, scan_id)
    if scan is None:
        raise AppError(code=SCAN_NOT_FOUND, message="Scan not found", status_code=404)
    out = scan_service.scan_to_schema(scan)
    if out.content is None:
        raise AppError(code=CONTENT_NOT_FOUND, message="Content not found", status_code=404)
    return out.content.model_dump()
