"""Exception handlers that emit structured error payloads."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from praevis_api.core.errors import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    AppError,
    error_body,
)
from praevis_api.core.logging import log_extra

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _headers(request_id: str | None) -> dict[str, str] | None:
    if not request_id:
        return None
    return {"X-Request-ID": request_id}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = _request_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(code=exc.code, message=exc.message, request_id=request_id),
            headers=_headers(request_id),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = _request_id(request)
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            code = str(detail["code"])
            message = str(detail.get("message") or code)
        else:
            code = str(detail) if isinstance(detail, str) else "http_error"
            message = code.replace("_", " ")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(code=code, message=message, request_id=request_id),
            headers=_headers(request_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = _request_id(request)
        fields = []
        for err in exc.errors()[:10]:
            loc = ".".join(str(part) for part in err.get("loc", ()))
            fields.append(f"{loc}: {err.get('msg', 'invalid')}")
        message = "; ".join(fields) if fields else "Request validation failed"
        return JSONResponse(
            status_code=422,
            content=error_body(code=VALIDATION_ERROR, message=message, request_id=request_id),
            headers=_headers(request_id),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        logger.exception(
            "unhandled error",
            extra=log_extra(request_id=request_id, outcome="error"),
        )
        _ = exc
        return JSONResponse(
            status_code=500,
            content=error_body(
                code=INTERNAL_ERROR,
                message="An unexpected error occurred",
                request_id=request_id,
            ),
            headers=_headers(request_id),
        )
