"""FastAPI application lifespan — startup and shutdown event handlers.

All infrastructure connections (DB, Redis, Elasticsearch) are opened on startup
and gracefully closed on shutdown, following RAII principles.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifetime — startup and shutdown."""
    await _startup()
    try:
        yield
    finally:
        await _shutdown()


async def _startup() -> None:
    """Run startup tasks: connect to infrastructure services."""
    logger.info("Starting AIvora Backend...")

    # Database connection pool
    try:
        from app.infrastructure.database.engine import engine

        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)  # ping
        logger.info("Database connection established")
    except Exception as exc:
        logger.error("Failed to connect to database", error=str(exc))
        raise

    # Redis connection
    try:
        from app.infrastructure.cache.redis_client import get_redis_client

        redis = await get_redis_client()
        await redis.ping()
        logger.info("Redis connection established")
    except Exception as exc:
        logger.warning("Redis connection failed — cache unavailable", error=str(exc))

    # Elasticsearch (non-fatal — may not be running during early development)
    try:
        from app.infrastructure.search.elasticsearch_client import get_elasticsearch_client

        es = await get_elasticsearch_client()
        await es.ping()
        logger.info("Elasticsearch connection established")
    except Exception as exc:
        logger.warning("Elasticsearch not available", error=str(exc))

    logger.info("AIvora Backend started successfully")


async def _shutdown() -> None:
    """Run shutdown tasks: close all infrastructure connections."""
    logger.info("Shutting down AIvora Backend...")

    try:
        from app.infrastructure.database.engine import engine

        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as exc:
        logger.warning("Error closing database connection", error=str(exc))

    try:
        from app.infrastructure.cache.redis_client import close_redis_client

        await close_redis_client()
        logger.info("Redis connection closed")
    except Exception as exc:
        logger.warning("Error closing Redis connection", error=str(exc))

    logger.info("AIvora Backend shut down gracefully")
