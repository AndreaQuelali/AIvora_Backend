"""Organizations router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_id
from app.schemas.common import StandardResponse
from app.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=StandardResponse[OrganizationResponse], status_code=201)
async def create_organization(
    body: OrganizationCreateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> StandardResponse[OrganizationResponse]:
    """Create a new organization."""
    raise NotImplementedError("OrganizationService not yet implemented.")


@router.get("/{org_id}", response_model=StandardResponse[OrganizationResponse])
async def get_organization(
    org_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> StandardResponse[OrganizationResponse]:
    """Get an organization by ID."""
    raise NotImplementedError("OrganizationService not yet implemented.")


@router.put("/{org_id}", response_model=StandardResponse[OrganizationResponse])
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> StandardResponse[OrganizationResponse]:
    """Update an organization."""
    raise NotImplementedError("OrganizationService not yet implemented.")


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    """Delete an organization and all its data."""
    raise NotImplementedError("OrganizationService not yet implemented.")
