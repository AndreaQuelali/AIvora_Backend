"""FastAPI auth dependencies — current user resolution from JWT."""

from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.exceptions.base import UnauthorizedError
from app.security.jwt import decode_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> uuid.UUID:
    """Extract and validate the JWT, returning the authenticated user's UUID.

    Raises:
        UnauthorizedError: If no token provided or token is invalid.
    """
    if credentials is None:
        raise UnauthorizedError("Bearer token is required.")
    payload = decode_token(credentials.credentials)
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise UnauthorizedError("Invalid token subject.")
    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise UnauthorizedError("Invalid user ID in token.") from exc
