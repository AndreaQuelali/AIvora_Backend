"""Security headers middleware — adds OWASP-recommended HTTP security headers."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every HTTP response.

    Headers applied:
    - ``X-Content-Type-Options: nosniff`` — prevent MIME sniffing
    - ``X-Frame-Options: DENY`` — prevent clickjacking
    - ``X-XSS-Protection: 1; mode=block`` — legacy XSS filter
    - ``Referrer-Policy: strict-origin-when-cross-origin``
    - ``Permissions-Policy`` — disable unused browser features
    - ``Strict-Transport-Security`` — enforce HTTPS (omitted in local)
    """

    def __init__(self, app: object, *, is_production: bool = False) -> None:
        super().__init__(app)
        self._is_production = is_production

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        )
        if self._is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response
