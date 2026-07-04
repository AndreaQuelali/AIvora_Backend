"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def app():
    """Create a test FastAPI app instance."""
    # Clear settings cache to avoid polluting test env
    from app.config.settings import get_settings
    get_settings.cache_clear()

    from app.core.app import create_app
    return create_app()


@pytest.fixture
def client(app):
    """Sync test client for simple endpoint tests."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
async def async_client(app):
    """Async test client for async endpoint tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
