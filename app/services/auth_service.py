"""Authentication service — coordinates login, token checks, and refresh."""

from __future__ import annotations

import uuid

from app.domain.user.entity import Email
from app.exceptions.base import UnauthorizedError
from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.models import TokenPair
from app.security.password import verify_password


class AuthService:
    """Service handling multi-tenant user authentication and registration workflows."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate user credentials and return a new JWT TokenPair."""
        user = await self._user_repo.get_by_email(Email(email))
        if not user:
            raise UnauthorizedError("Incorrect email or password.")

        if not verify_password(password, user.hashed_password.value):
            raise UnauthorizedError("Incorrect email or password.")

        # Create access claims (useful for tenant isolation and RBAC directly in JWT)
        claims = {
            "org_id": str(user.organization_id) if user.organization_id else None,
            "is_superuser": user.is_superuser,
        }
        access_token = create_access_token(subject=str(user.id), extra_claims=claims)
        refresh_token = create_refresh_token(subject=str(user.id))

        from app.config.settings import get_settings

        settings = get_settings()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt.access_token_expire_minutes * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Exchange a refresh token for a fresh access/refresh token pair.

        Ensures security by verifying token type and active user checks.
        """
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type.")

        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedError("Invalid token payload.")

        user_id = uuid.UUID(sub)
        user = await self._user_repo.get_by_id(user_id)
        if not user or user.status.value == "suspended":
            raise UnauthorizedError("User is suspended or doesn't exist.")

        claims = {
            "org_id": str(user.organization_id) if user.organization_id else None,
            "is_superuser": user.is_superuser,
        }
        new_access = create_access_token(subject=str(user.id), extra_claims=claims)
        new_refresh = create_refresh_token(subject=str(user.id))

        from app.config.settings import get_settings

        settings = get_settings()

        return TokenPair(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.jwt.access_token_expire_minutes * 60,
        )
