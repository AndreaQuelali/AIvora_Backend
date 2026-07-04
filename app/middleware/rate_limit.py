"""Rate limiting middleware — Redis-backed sliding-window rate limiter.

Uses ``slowapi`` (a Starlette-compatible wrapper around ``limits``) to limit
requests per IP and optionally per authenticated user.

Configuration comes from ``RateLimitSettings`` and is applied globally.
Route-level overrides are possible via the ``@limiter.limit(...)`` decorator.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.config.settings import get_settings

_settings = get_settings()

# The limiter instance is exposed so individual routes can apply custom limits
# via: @router.get("/endpoint", dependencies=[Depends(limiter.limit("5/minute"))])
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_settings.rate_limit.default] if _settings.rate_limit.enabled else [],
    storage_uri=_settings.redis.url,
    enabled=_settings.rate_limit.enabled,
)


def register_rate_limiter(app: FastAPI) -> None:
    """Attach the rate limiter and its exception handler to the FastAPI app."""
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", "")
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "detail": str(exc.detail),
                },
                "request_id": request_id,
            },
            headers={"Retry-After": "60"},
        )
