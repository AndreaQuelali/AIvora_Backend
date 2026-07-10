"""Generic base repository with common CRUD operations (SQLAlchemy 2.0 async)."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async SQLAlchemy repository.

    Subclasses must set the ``model`` class attribute.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, record_id: uuid.UUID) -> ModelT | None:
        """Fetch a single record by primary key."""
        return await self._session.get(self.model, record_id)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelT]:
        """List records with optional equality filters and pagination."""
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, instance: ModelT) -> ModelT:
        """Persist a new record."""
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, instance: ModelT) -> ModelT:
        """Update an existing record."""
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete a record permanently."""
        await self._session.delete(instance)
        await self._session.flush()

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count records matching optional filters."""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await self._session.execute(stmt)
        return result.scalar_one()
