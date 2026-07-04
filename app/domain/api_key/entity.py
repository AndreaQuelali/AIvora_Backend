"""API Key domain aggregate."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.base import AggregateRoot, IRepository


@dataclass
class ApiKeyEntity(AggregateRoot):
    """API Key aggregate root.

    API keys allow programmatic access without user sessions.
    Only the hash is stored; the plaintext is shown once on creation.

    Attributes:
        organization_id: Owning organization.
        user_id: Creator user.
        name: Human-readable label.
        key_hash: SHA-256 hash of the raw key.
        prefix: First 8 chars of key shown in UI (e.g., 'aiv_abc1').
        is_active: Can be revoked without deletion.
        expires_at: Optional expiry datetime.
        last_used_at: Last successful authentication.
        scopes: Granted permission scopes.
    """

    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    name: str = ""
    key_hash: str = ""
    prefix: str = ""
    is_active: bool = True
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    scopes: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        scopes: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> tuple["ApiKeyEntity", str]:
        """Create a new API key, returning the entity and the plaintext key.

        The plaintext key is returned ONCE and never stored.
        """
        raw_key = f"aiv_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        entity = cls(
            organization_id=organization_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=raw_key[:8],
            scopes=scopes or [],
            expires_at=expires_at,
        )
        return entity, raw_key

    def revoke(self) -> None:
        """Deactivate this API key."""
        self.is_active = False
        self.touch()

    @property
    def is_expired(self) -> bool:
        """Return True if the key has passed its expiry datetime."""
        if self.expires_at is None:
            return False
        from app.domain.base import utcnow
        return utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Return True if the key can be used for authentication."""
        return self.is_active and not self.is_expired

    @staticmethod
    def hash_raw_key(raw_key: str) -> str:
        """Hash a raw API key for lookup."""
        return hashlib.sha256(raw_key.encode()).hexdigest()


class IApiKeyRepository(IRepository[ApiKeyEntity]):
    """Abstract API key repository."""

    @abstractmethod
    async def get_by_id(self, key_id: uuid.UUID) -> ApiKeyEntity | None: ...

    @abstractmethod
    async def get_by_hash(self, key_hash: str) -> ApiKeyEntity | None: ...

    @abstractmethod
    async def list_by_organization(self, organization_id: uuid.UUID) -> list[ApiKeyEntity]: ...

    @abstractmethod
    async def save(self, api_key: ApiKeyEntity) -> ApiKeyEntity: ...

    @abstractmethod
    async def delete(self, key_id: uuid.UUID) -> None: ...
