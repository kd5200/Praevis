"""Structured application errors and API error payloads."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def error_body(*, code: str, message: str, request_id: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": message}
    if request_id:
        payload["request_id"] = request_id
    return {"error": payload}


# Common API error codes (documented in docs/API_SPEC.md)
SCAN_NOT_FOUND = "scan_not_found"
CONTENT_NOT_FOUND = "content_not_found"
VALIDATION_ERROR = "validation_error"
RATE_LIMITED = "rate_limited"
REQUEST_TOO_LARGE = "request_too_large"
INTERNAL_ERROR = "internal_error"
