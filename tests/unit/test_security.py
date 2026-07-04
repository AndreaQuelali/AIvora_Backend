"""Unit tests for security utilities — JWT and password hashing."""

from __future__ import annotations

import uuid

import pytest

from app.exceptions.base import TokenExpiredError, TokenInvalidError
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hash_password_produces_different_hash_each_time() -> None:
    """bcrypt uses a random salt, so two hashes of the same password differ."""
    pw = "super_secret_123"
    assert hash_password(pw) != hash_password(pw)


@pytest.mark.unit
def test_verify_password_correct() -> None:
    """Correct password verifies against its hash."""
    pw = "my_password_456"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


@pytest.mark.unit
def test_verify_password_wrong() -> None:
    """Wrong password does not verify."""
    hashed = hash_password("correct_password")
    assert verify_password("wrong_password", hashed) is False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_create_and_decode_access_token() -> None:
    """Access token round-trip: create → decode → same subject."""
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


@pytest.mark.unit
def test_create_and_decode_refresh_token() -> None:
    """Refresh token type is 'refresh'."""
    user_id = str(uuid.uuid4())
    token = create_refresh_token(subject=user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


@pytest.mark.unit
def test_decode_invalid_token_raises() -> None:
    """Decoding a garbage string raises TokenInvalidError."""
    with pytest.raises(TokenInvalidError):
        decode_token("not.a.valid.jwt")


@pytest.mark.unit
def test_access_token_extra_claims() -> None:
    """Extra claims are preserved in the decoded payload."""
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id, extra_claims={"org_id": org_id})
    payload = decode_token(token)
    assert payload["org_id"] == org_id
