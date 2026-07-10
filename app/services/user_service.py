"""User service — manages user accounts and profiles."""

from __future__ import annotations

import uuid

from app.domain.user.entity import Email, HashedPassword, UserEntity
from app.exceptions.base import ConflictError, NotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from app.security.password import hash_password


class UserService:
    """Manages User account CRUD & checks email uniqueness."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Fetch user by primary key, or raise NotFoundError."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found.")
        return UserResponse.model_validate(user)

    async def register_user(self, request: UserCreateRequest) -> UserResponse:
        """Register a new user inside an organization."""
        email = Email(request.email)
        if await self._user_repo.exists_by_email(email):
            raise ConflictError(f"Email {request.email} is already registered.")

        hashed = HashedPassword(hash_password(request.password))
        user = UserEntity.register(
            email=email,
            password=hashed,
            full_name=request.full_name,
            organization_id=request.organization_id,
        )
        await self._user_repo.save(user)
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: uuid.UUID, request: UserUpdateRequest) -> UserResponse:
        """Update user profile meta information."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found.")

        if request.full_name is not None:
            user.full_name = request.full_name

        user.touch()
        await self._user_repo.save(user)
        return UserResponse.model_validate(user)

    async def list_users_by_organization(
        self, organization_id: uuid.UUID, *, page: int = 1, page_size: int = 20
    ) -> list[UserResponse]:
        """List active members of a tenant organization."""
        offset = (page - 1) * page_size
        users = await self._user_repo.list_by_organization(
            organization_id, offset=offset, limit=page_size
        )
        return [UserResponse.model_validate(u) for u in users]
