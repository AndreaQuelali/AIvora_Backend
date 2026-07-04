"""User schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
    organization_id: uuid.UUID | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    status: str
    is_superuser: bool
    organization_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
