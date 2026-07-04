"""Concrete Audit Log repository implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit.entity import AuditAction, AuditLogEntity, IAuditRepository
from app.infrastructure.models.audit_log import AuditLogModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class AuditRepository(BaseRepository[AuditLogModel], IAuditRepository):
    """SQLAlchemy implementation of the IAuditRepository interface."""

    model = AuditLogModel

    async def append(self, log: AuditLogEntity) -> AuditLogEntity:
        model = DataMapper.audit_to_model(log)
        await self.create(model)
        return log

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        actor_id: uuid.UUID | None = None,
        action: AuditAction | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[AuditLogEntity]:
        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.organization_id == organization_id)
            .order_by(AuditLogModel.created_at.desc())
        )
        if actor_id:
            stmt = stmt.where(AuditLogModel.actor_id == actor_id)
        if action:
            stmt = stmt.where(AuditLogModel.action == action.value)

        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [DataMapper.audit_to_entity(m) for m in result.scalars().all()]
