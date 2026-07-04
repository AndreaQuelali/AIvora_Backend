"""Security package token models."""

from __future__ import annotations

from pydantic import BaseModel


class TokenPair(BaseModel):
    """Access + refresh token pair returned at login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""

    sub: str          # user ID
    exp: int          # expiry timestamp
    iat: int          # issued-at timestamp
    type: str         # "access" | "refresh"
    org_id: str | None = None
    roles: list[str] = []
