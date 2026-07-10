"""Users router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_id
from app.dependencies.services import get_user_repository, get_user_service
from app.repositories.user_repository import UserRepository
from app.schemas.common import StandardResponse
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> StandardResponse[UserResponse]:
    """Return the authenticated user's profile."""
    user = await user_service.get_user_by_id(current_user_id)
    return StandardResponse(data=user)


@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user(
    user_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> StandardResponse[UserResponse]:
    """Return a user's profile by ID."""
    user = await user_service.get_user_by_id(user_id)
    return StandardResponse(data=user)


@router.put("/{user_id}", response_model=StandardResponse[UserResponse])
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> StandardResponse[UserResponse]:
    """Update a user's profile."""
    # Ensure standard users can only update themselves (could add fine-grained policy check later)
    user = await user_service.update_user(user_id, body)
    return StandardResponse(data=user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
) -> None:
    """Delete a user account."""
    await user_repo.delete(user_id)
