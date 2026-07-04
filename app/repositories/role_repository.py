"""Concrete Role and Permission repositories implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.role.entity import IPermissionRepository, IRoleRepository, PermissionEntity, RoleEntity
from app.infrastructure.models.role import PermissionModel, RoleModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class RoleRepository(BaseRepository[RoleModel], IRoleRepository):
    """SQLAlchemy implementation of the IRoleRepository interface."""

    model = RoleModel

    async def get_by_id(self, role_id: uuid.UUID) -> RoleEntity | None:
        stmt = (
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(selectinload(RoleModel.permissions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.role_to_entity(model) if model else None

    async def get_by_name(
        self, name: str, *, organization_id: uuid.UUID | None = None
    ) -> RoleEntity | None:
        stmt = (
            select(RoleModel)
            .where(RoleModel.name == name, RoleModel.organization_id == organization_id)
            .options(selectinload(RoleModel.permissions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.role_to_entity(model) if model else None

    async def list_all(
        self, *, organization_id: uuid.UUID | None = None
    ) -> list[RoleEntity]:
        stmt = (
            select(RoleModel)
            .where(RoleModel.organization_id == organization_id)
            .options(selectinload(RoleModel.permissions))
        )
        result = await self._session.execute(stmt)
        return [DataMapper.role_to_entity(m) for m in result.scalars().all()]

    async def save(self, role: RoleEntity) -> RoleEntity:
        stmt = select(RoleModel).where(RoleModel.id == role.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.role_to_model(role)
            existing_model.name = model.name
            existing_model.description = model.description
            existing_model.updated_at = role.updated_at
            # Permissions additions/removals would be handled via session relations
            await self._session.flush()
            return role
        else:
            model = DataMapper.role_to_model(role)
            await self.create(model)
            return role

    async def delete(self, role_id: uuid.UUID) -> None:
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()


class PermissionRepository(BaseRepository[PermissionModel], IPermissionRepository):
    """SQLAlchemy implementation of the IPermissionRepository interface."""

    model = PermissionModel

    async def get_by_id(self, perm_id: uuid.UUID) -> PermissionEntity | None:
        stmt = select(PermissionModel).where(PermissionModel.id == perm_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.permission_to_entity(model) if model else None

    async def get_by_code(self, code: str) -> PermissionEntity | None:
        if ":" not in code:
            return None
        resource, action = code.split(":", 1)
        stmt = select(PermissionModel).where(
            PermissionModel.resource == resource, PermissionModel.action == action
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.permission_to_entity(model) if model else None

    async def list_all(self) -> list[PermissionEntity]:
        stmt = select(PermissionModel)
        result = await self._session.execute(stmt)
        return [DataMapper.permission_to_entity(m) for m in result.scalars().all()]

    async def save(self, permission: PermissionEntity) -> PermissionEntity:
        stmt = select(PermissionModel).where(PermissionModel.id == permission.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.permission_to_model(permission)
            existing_model.name = model.name
            existing_model.description = model.description
            existing_model.resource = model.resource
            existing_model.action = model.action
            existing_model.updated_at = permission.updated_at
            await self._session.flush()
            return permission
        else:
            model = DataMapper.permission_to_model(permission)
            await self.create(model)
            return permission
