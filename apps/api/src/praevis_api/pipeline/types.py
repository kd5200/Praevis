"""Typed pipeline inputs/outputs and shared finding records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PipelineFinding:
    category: str
    severity: str
    detector: str
    title: str
    description: str
    evidence: str | None = None
    remediation: str | None = None
    confidence: float = 1.0


@dataclass(slots=True)
class NormalizedUrl:
    original: str
    normalized: str
    scheme: str
    host: str
    port: int | None
    path: str


@dataclass(slots=True)
class DestinationInfo:
    url: str
    host: str
    resolved_ips: list[str]
    is_https: bool


@dataclass(slots=True)
class FetchResult:
    final_url: str
    status_code: int
    content_type: str
    body: bytes
    redirect_chain: list[str]
    retrieved_at: datetime
    content_hash: str


@dataclass(slots=True)
class ExtractedContent:
    title: str | None
    text: str
    html: str
    language: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScoreResult:
    risk_score: int
    trust_score: int
    decision: str
    explanation: dict[str, Any]


@dataclass(slots=True)
class PipelineResult:
    status: str
    submitted_url: str
    normalized_url: str | None
    final_url: str | None
    risk_score: int | None
    trust_score: int | None
    decision: str | None
    findings: list[PipelineFinding]
    content: ExtractedContent | None
    content_hash: str | None
    redirect_chain: list[str]
    raw_content_reference: str | None
    content_type: str | None
    score_explanation: dict[str, Any] | None
    error_code: str | None = None
    error_message: str | None = None
    retrieved_at: datetime | None = None
