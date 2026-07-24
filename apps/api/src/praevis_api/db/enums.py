"""Shared domain enums."""

from __future__ import annotations

from enum import StrEnum


class ScanStatus(StrEnum):
    QUEUED = "queued"
    VALIDATING = "validating"
    FETCHING = "fetching"
    ANALYZING = "analyzing"
    SANITIZING = "sanitizing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class Decision(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingCategory(StrEnum):
    PROMPT_INJECTION = "prompt_injection"
    SSRF = "ssrf"
    REDIRECT = "redirect"
    CONTENT = "content"
    TRANSPORT = "transport"
    POLICY = "policy"
