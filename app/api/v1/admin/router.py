"""Admin router — platform administration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies.auth import get_current_user_id
from app.dependencies.pagination import PaginationParams, get_pagination

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def admin_list_users(
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id = Depends(get_current_user_id),  # noqa: ANN001
) -> dict:
    """List all users (superuser only)."""
    raise NotImplementedError("Admin service not yet implemented.")


@router.get("/audit-logs")
async def admin_list_audit_logs(
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id = Depends(get_current_user_id),  # noqa: ANN001
) -> dict:
    """List all audit logs (superuser only)."""
    raise NotImplementedError("Admin service not yet implemented.")


@router.get("/organizations")
async def admin_list_organizations(
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id = Depends(get_current_user_id),  # noqa: ANN001
) -> dict:
    """List all organizations (superuser only)."""
    raise NotImplementedError("Admin service not yet implemented.")
