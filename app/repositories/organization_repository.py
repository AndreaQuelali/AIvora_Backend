"""Concrete organization repository implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.domain.organization.entity import IOrganizationRepository, OrganizationEntity, Slug
from app.infrastructure.models.organization import OrganizationModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class OrganizationRepository(BaseRepository[OrganizationModel], IOrganizationRepository):
    """SQLAlchemy implementation of the IOrganizationRepository interface."""

    model = OrganizationModel

    async def get_by_id(self, org_id: uuid.UUID) -> OrganizationEntity | None:  # type: ignore[override]
        stmt = select(OrganizationModel).where(
            OrganizationModel.id == org_id,
            OrganizationModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.org_to_entity(model) if model else None

    async def get_by_slug(self, slug: Slug) -> OrganizationEntity | None:
        stmt = select(OrganizationModel).where(
            OrganizationModel.slug == str(slug),
            OrganizationModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.org_to_entity(model) if model else None

    async def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[OrganizationEntity]:
        stmt = (
            select(OrganizationModel)
            .where(OrganizationModel.deleted_at.is_(None))
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [DataMapper.org_to_entity(m) for m in result.scalars().all()]

    async def save(self, org: OrganizationEntity) -> OrganizationEntity:
        stmt = select(OrganizationModel).where(OrganizationModel.id == org.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.org_to_model(org)
            for attr in (
                "name",
                "slug",
                "plan",
                "status",
                "owner_id",
                "max_users",
                "max_documents",
            ):
                setattr(existing_model, attr, getattr(model, attr))
            existing_model.updated_at = org.updated_at
            await self._session.flush()
            return org
        else:
            model = DataMapper.org_to_model(org)
            await self.create(model)
            return org

    async def delete(self, org_id: uuid.UUID) -> None:  # type: ignore[override]
        stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            from app.domain.base import utcnow

            model.deleted_at = utcnow()
            await self._session.flush()
