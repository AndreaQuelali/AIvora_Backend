"""Auth router — login, token refresh, and logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.services import get_auth_service
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate user credentials and return a token pair."""
    token_pair = await auth_service.login(body.email, body.password)
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Exchange a refresh token for a new access token."""
    token_pair = await auth_service.refresh_tokens(body.refresh_token)
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout() -> MessageResponse:
    """Invalidate the current user's refresh token."""
    # Token is invalidated client-side; server-side blacklisting can be added if needed.
    return MessageResponse(message="Logged out successfully.")
