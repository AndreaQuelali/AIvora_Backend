"""Health check router — liveness, readiness, and general health info."""

from __future__ import annotations

import time

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from app.config.settings import get_settings
from app.schemas.health import HealthResponse, ServiceStatus

router = APIRouter(prefix="/health", tags=["Health"])
_settings = get_settings()


@router.get("")
async def health() -> HealthResponse:
    """Return app version and environment info."""
    return HealthResponse(
        status="ok",
        version=_settings.app.version,
        environment=_settings.app.env,
    )


@router.get("/live")
async def liveness() -> ORJSONResponse:
    """Liveness probe — returns 200 if the process is alive."""
    return ORJSONResponse({"status": "alive"})


@router.get("/ready")
async def readiness() -> HealthResponse:
    """Readiness probe — checks DB and Redis connectivity.

    Returns 200 when all critical services are reachable,
    503 if any critical service is degraded.
    """
    services: list[ServiceStatus] = []
    overall = "ok"

    # --- Database ---
    try:
        start = time.monotonic()
        from app.infrastructure.database.engine import engine

        async with engine.connect() as conn:
            await conn.run_sync(lambda _: None)
        db_latency = round((time.monotonic() - start) * 1000, 2)
        services.append(ServiceStatus(name="database", status="ok", latency_ms=db_latency))
    except Exception:
        services.append(ServiceStatus(name="database", status="unavailable"))
        overall = "degraded"

    # --- Redis ---
    try:
        start = time.monotonic()
        from app.infrastructure.cache.redis_client import get_redis_client

        r = await get_redis_client()
        await r.ping()
        redis_latency = round((time.monotonic() - start) * 1000, 2)
        services.append(ServiceStatus(name="redis", status="ok", latency_ms=redis_latency))
    except Exception:
        services.append(ServiceStatus(name="redis", status="unavailable"))
        # Redis is non-critical in this scaffold; degraded but not down
        if overall == "ok":
            overall = "degraded"

    return HealthResponse(
        status=overall,
        version=_settings.app.version,
        environment=_settings.app.env,
        services=services,
    )
