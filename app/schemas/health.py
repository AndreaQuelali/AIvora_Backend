"""Health check schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    name: str
    status: str  # "ok" | "degraded" | "unavailable"
    latency_ms: float | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: list[ServiceStatus] = []
