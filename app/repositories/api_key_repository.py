"""Concrete API Key repository implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.domain.api_key.entity import ApiKeyEntity, IApiKeyRepository
from app.infrastructure.models.api_key import ApiKeyModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class ApiKeyRepository(BaseRepository[ApiKeyModel], IApiKeyRepository):
    """SQLAlchemy implementation of the IApiKeyRepository interface."""

    model = ApiKeyModel

    async def get_by_id(self, key_id: uuid.UUID) -> ApiKeyEntity | None:  # type: ignore[override]
        stmt = select(ApiKeyModel).where(ApiKeyModel.id == key_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.api_key_to_entity(model) if model else None

    async def get_by_hash(self, key_hash: str) -> ApiKeyEntity | None:
        stmt = select(ApiKeyModel).where(
            ApiKeyModel.key_hash == key_hash,
            ApiKeyModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.api_key_to_entity(model) if model else None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[ApiKeyEntity]:
        stmt = select(ApiKeyModel).where(ApiKeyModel.organization_id == organization_id)
        result = await self._session.execute(stmt)
        return [DataMapper.api_key_to_entity(m) for m in result.scalars().all()]

    async def save(self, api_key: ApiKeyEntity) -> ApiKeyEntity:
        stmt = select(ApiKeyModel).where(ApiKeyModel.id == api_key.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.api_key_to_model(api_key)
            existing_model.is_active = model.is_active
            existing_model.last_used_at = model.last_used_at
            existing_model.updated_at = api_key.updated_at
            await self._session.flush()
            return api_key
        else:
            model = DataMapper.api_key_to_model(api_key)
            await self.create(model)
            return api_key

    async def delete(self, key_id: uuid.UUID) -> None:  # type: ignore[override]
        stmt = select(ApiKeyModel).where(ApiKeyModel.id == key_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
