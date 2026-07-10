"""FastAPI dependency — provides an async DB session per request."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.engine import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield an ``AsyncSession`` for the request's lifetime.

    The session is automatically committed on success and rolled back on error.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
