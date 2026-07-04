"""JWT token utilities — create, decode, and validate access/refresh tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config.settings import get_settings
from app.exceptions.base import TokenExpiredError, TokenInvalidError

_settings = get_settings()


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Usually the user's UUID string.
        extra_claims: Additional claims to embed (e.g., org_id, roles).

    Returns:
        Signed JWT string.
    """
    expire = _utcnow() + timedelta(minutes=_settings.jwt.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": _utcnow(),
        "type": "access",
        **(extra_claims or {}),
    }
    return jwt.encode(payload, _settings.jwt.secret_key, algorithm=_settings.jwt.algorithm)


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token.

    Refresh tokens have a longer TTL and fewer claims.
    """
    expire = _utcnow() + timedelta(days=_settings.jwt.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": _utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, _settings.jwt.secret_key, algorithm=_settings.jwt.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token.

    Raises:
        TokenExpiredError: If the token has expired.
        TokenInvalidError: If the token is malformed or signature invalid.
    """
    try:
        payload = jwt.decode(
            token,
            _settings.jwt.secret_key,
            algorithms=[_settings.jwt.algorithm],
        )
        return dict(payload)
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredError from exc
        raise TokenInvalidError from exc


def get_token_subject(token: str) -> str:
    """Extract the ``sub`` claim from a token without fully re-verifying."""
    payload = decode_token(token)
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise TokenInvalidError
    return sub
