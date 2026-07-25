"""HTTP middleware: request id, timing, basic body-size / rate limits."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from praevis_api.core.config import get_settings
from praevis_api.core.errors import RATE_LIMITED, REQUEST_TOO_LARGE, error_body
from praevis_api.core.logging import log_extra
from praevis_api.core.rate_limit import rate_limiter

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        settings = get_settings()
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id

        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > settings.max_request_body_bytes:
                    return JSONResponse(
                        status_code=413,
                        content=error_body(
                            code=REQUEST_TOO_LARGE,
                            message="Request body exceeds configured size limit",
                            request_id=request_id,
                        ),
                        headers={REQUEST_ID_HEADER: request_id},
                    )
            except ValueError:
                pass

        client_host = request.client.host if request.client else "unknown"
        # Only rate-limit mutating scan creation; keep reads/health unrestricted.
        if request.method == "POST" and request.url.path.rstrip("/") == "/v1/scans":
            if not rate_limiter.allow(
                f"scan-create:{client_host}",
                limit=settings.rate_limit_per_minute,
            ):
                return JSONResponse(
                    status_code=429,
                    content=error_body(
                        code=RATE_LIMITED,
                        message="Scan creation rate limit exceeded",
                        request_id=request_id,
                    ),
                    headers={REQUEST_ID_HEADER: request_id, "Retry-After": "60"},
                )

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "request failed",
                extra=log_extra(
                    request_id=request_id,
                    duration_ms=duration_ms,
                    outcome="error",
                ),
            )
            raise

        duration_ms = (time.perf_counter() - started) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"
        logger.info(
            "request completed",
            extra=log_extra(
                request_id=request_id,
                duration_ms=duration_ms,
                outcome=str(response.status_code),
            ),
        )
        # Attach method/path via standard logger message context only (avoid body/PII).
        logger.debug("%s %s", request.method, request.url.path)
        return response
