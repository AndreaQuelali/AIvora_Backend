"""Smoke tests for health endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_returns_ok(client: TestClient) -> None:
    """GET /api/v1/health should return 200 with status=ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.unit
def test_liveness_returns_200(client: TestClient) -> None:
    """GET /api/v1/health/live should always return 200."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.unit
def test_openapi_schema_accessible(client: TestClient) -> None:
    """GET /openapi.json should return a valid OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
