"""Request ID middleware — injects a unique X-Request-ID on every request/response.

The request ID is:
  1. Taken from the incoming ``X-Request-ID`` header if present (useful for tracing
     across service boundaries).
  2. Generated as a new ULID if not provided.

The ID is added to structlog's context vars so it appears in every log line
emitted during that request's lifecycle.
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID into each request context and response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Bind to structlog context so all log lines within this request carry it
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
