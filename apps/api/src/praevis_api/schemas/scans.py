"""Pydantic schemas for scan API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ScanCreateRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    mode: Literal["standard"] = "standard"
    wait_for_completion: bool = True


class FindingOut(BaseModel):
    id: uuid.UUID | None = None
    category: str
    severity: str
    detector: str
    title: str
    description: str
    evidence: str | None = None
    remediation: str | None = None
    confidence: float


class ContentOut(BaseModel):
    title: str | None = None
    text: str | None = None
    content_type: str | None = None
    sanitized_html: str | None = None


class ProvenanceOut(BaseModel):
    retrieved_at: datetime | None = None
    content_hash: str | None = None  # original retrieved body; prefer integrity.original
    original_content_hash: str | None = None
    sanitized_content_hash: str | None = None
    redirect_chain: list[str] = Field(default_factory=list)
    requested_url: str | None = None
    normalized_url: str | None = None
    final_url: str | None = None


class IntegrityOut(BaseModel):
    """Content integrity fields for agent retrieval receipts."""

    original_content_hash: str | None = None
    sanitized_content_hash: str | None = None


class ScanOut(BaseModel):
    scan_id: uuid.UUID
    status: str
    submitted_url: str
    normalized_url: str | None = None
    final_url: str | None = None
    risk_score: int | None = None
    trust_score: int | None = None
    decision: str | None = None
    findings: list[FindingOut] = Field(default_factory=list)
    content: ContentOut | None = None
    provenance: ProvenanceOut | None = None
    integrity: IntegrityOut | None = None
    score_explanation: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


class ScanListOut(BaseModel):
    items: list[ScanOut]
    total: int
