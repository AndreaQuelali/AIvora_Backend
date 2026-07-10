"""Concrete user repository implementation using SQLAlchemy 2.0 async and PostgreSQL."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.user.entity import Email, IUserRepository, UserEntity
from app.infrastructure.models.user import UserModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class UserRepository(BaseRepository[UserModel], IUserRepository):
    """SQLAlchemy implementation of the IUserRepository interface."""

    model = UserModel

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:  # type: ignore[override]
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
            .options(selectinload(UserModel.roles))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.user_to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> UserEntity | None:
        stmt = (
            select(UserModel)
            .where(UserModel.email == str(email), UserModel.deleted_at.is_(None))
            .options(selectinload(UserModel.roles))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.user_to_entity(model) if model else None

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[UserEntity]:
        stmt = (
            select(UserModel)
            .where(
                UserModel.organization_id == organization_id,
                UserModel.deleted_at.is_(None),
            )
            .options(selectinload(UserModel.roles))
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [DataMapper.user_to_entity(m) for m in result.scalars().all()]

    async def save(self, user: UserEntity) -> UserEntity:
        # Check if record already exists to perform update vs create
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            # Map updated attributes from entity to existing model instance
            model = DataMapper.user_to_model(user)
            for attr in ("email", "hashed_password", "full_name", "status", "is_superuser"):
                setattr(existing_model, attr, getattr(model, attr))
            existing_model.updated_at = user.updated_at
            # Note: Role updates would be managed via relation associations here
            await self._session.flush()
            return user
        else:
            model = DataMapper.user_to_model(user)
            await self.create(model)
            return user

    async def delete(self, user_id: uuid.UUID) -> None:  # type: ignore[override]
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            from app.domain.base import utcnow

            model.deleted_at = utcnow()
            await self._session.flush()

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel).where(
            UserModel.email == str(email),
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
