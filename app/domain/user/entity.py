"""User aggregate — entity, value objects, domain events, repository interface."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.base import AggregateRoot, DomainEvent, IRepository, ValueObject


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Email(ValueObject):
    """Email address value object — guarantees lowercase normalization."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)
        if "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise ValueError(f"Invalid email address: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HashedPassword(ValueObject):
    """Hashed password value object — wraps bcrypt hash, never stores plaintext."""

    value: str


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class UserStatus(StrEnum):
    """User lifecycle status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


# ---------------------------------------------------------------------------
# Domain Events
# ---------------------------------------------------------------------------


@dataclass
class UserCreatedEvent(DomainEvent):
    """Raised when a new user is registered."""

    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    organization_id: uuid.UUID | None = None


@dataclass
class UserActivatedEvent(DomainEvent):
    """Raised when a user completes email verification."""

    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class UserPasswordChangedEvent(DomainEvent):
    """Raised when a user changes their password."""

    user_id: uuid.UUID = field(default_factory=uuid.uuid4)


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------


@dataclass
class UserEntity(AggregateRoot):
    """User aggregate root.

    Attributes:
        email: Validated email address (value object).
        hashed_password: Bcrypt-hashed password (value object).
        full_name: Display name.
        organization_id: FK to Organization — None for super admins.
        role_ids: Set of assigned role IDs.
        status: Current lifecycle status.
        is_superuser: Bypasses all RBAC checks.
    """

    email: Email = field(default_factory=lambda: Email("placeholder@example.com"))
    hashed_password: HashedPassword = field(
        default_factory=lambda: HashedPassword("")
    )
    full_name: str = ""
    organization_id: uuid.UUID | None = None
    role_ids: set[uuid.UUID] = field(default_factory=set)
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    is_superuser: bool = False

    # ------------------------------------------------------------------
    # Factory Methods & Behavior
    # ------------------------------------------------------------------

    @classmethod
    def register(
        cls,
        email: Email,
        password: HashedPassword,
        full_name: str,
        organization_id: uuid.UUID | None = None,
        is_superuser: bool = False,
    ) -> UserEntity:
        """Create and register a new user, dispatching UserCreatedEvent."""
        user = cls(
            email=email,
            hashed_password=password,
            full_name=full_name,
            organization_id=organization_id,
            status=UserStatus.PENDING_VERIFICATION,
            is_superuser=is_superuser,
        )
        user.record_event(
            UserCreatedEvent(
                user_id=user.id,
                email=str(email),
                organization_id=organization_id,
            )
        )
        return user


    def activate(self) -> None:
        """Mark the user as active after email verification."""
        self.status = UserStatus.ACTIVE
        self.touch()
        self.record_event(UserActivatedEvent(user_id=self.id))

    def suspend(self) -> None:
        """Suspend the user account."""
        self.status = UserStatus.SUSPENDED
        self.touch()

    def change_password(self, new_hashed: HashedPassword) -> None:
        """Update the hashed password."""
        self.hashed_password = new_hashed
        self.touch()
        self.record_event(UserPasswordChangedEvent(user_id=self.id))

    def assign_role(self, role_id: uuid.UUID) -> None:
        """Assign a role to this user."""
        self.role_ids.add(role_id)
        self.touch()

    def revoke_role(self, role_id: uuid.UUID) -> None:
        """Remove a role from this user."""
        self.role_ids.discard(role_id)
        self.touch()

    @property
    def is_active(self) -> bool:
        """Return True if the user can authenticate."""
        return self.status == UserStatus.ACTIVE


# ---------------------------------------------------------------------------
# Repository Interface
# ---------------------------------------------------------------------------


class IUserRepository(IRepository[UserEntity]):
    """Abstract user repository — implemented in infrastructure layer."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> UserEntity | None: ...

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[UserEntity]: ...

    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity: ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool: ...
