"""Organization aggregate — entity, value objects, domain events, repository interface."""

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
class Slug(ValueObject):
    """URL-safe identifier for an organization (e.g., 'acme-corp')."""

    value: str

    def __post_init__(self) -> None:
        import re
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", self.value):
            raise ValueError(f"Invalid slug: {self.value!r}. Must be lowercase alphanumeric with hyphens.")

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class OrganizationPlan(StrEnum):
    """Subscription tier."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"


# ---------------------------------------------------------------------------
# Domain Events
# ---------------------------------------------------------------------------


@dataclass
class OrganizationCreatedEvent(DomainEvent):
    """Raised when a new organization is provisioned."""

    organization_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    owner_id: uuid.UUID | None = None


@dataclass
class OrganizationPlanChangedEvent(DomainEvent):
    """Raised when the subscription plan changes."""

    organization_id: uuid.UUID = field(default_factory=uuid.uuid4)
    old_plan: str = ""
    new_plan: str = ""


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------


@dataclass
class OrganizationEntity(AggregateRoot):
    """Organization aggregate root — represents a SaaS tenant.

    Attributes:
        name: Display name.
        slug: URL-safe unique identifier.
        plan: Current subscription plan.
        status: Lifecycle status.
        owner_id: User ID of the organization owner.
        max_users: Seat limit (plan-dependent).
        max_documents: Document storage limit.
    """

    name: str = ""
    slug: Slug = field(default_factory=lambda: Slug("default"))
    plan: OrganizationPlan = OrganizationPlan.FREE
    status: OrganizationStatus = OrganizationStatus.TRIAL
    owner_id: uuid.UUID | None = None
    max_users: int = 5
    max_documents: int = 100

    def upgrade_plan(self, new_plan: OrganizationPlan) -> None:
        """Upgrade or downgrade the organization's subscription plan."""
        old_plan = self.plan.value
        self.plan = new_plan
        self.touch()
        self.record_event(
            OrganizationPlanChangedEvent(
                organization_id=self.id,
                old_plan=old_plan,
                new_plan=new_plan.value,
            )
        )

    def suspend(self) -> None:
        """Suspend the organization (e.g., payment failure)."""
        self.status = OrganizationStatus.SUSPENDED
        self.touch()

    def activate(self) -> None:
        """Reactivate the organization."""
        self.status = OrganizationStatus.ACTIVE
        self.touch()


# ---------------------------------------------------------------------------
# Repository Interface
# ---------------------------------------------------------------------------


class IOrganizationRepository(IRepository[OrganizationEntity]):
    """Abstract organization repository."""

    @abstractmethod
    async def get_by_id(self, org_id: uuid.UUID) -> OrganizationEntity | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: Slug) -> OrganizationEntity | None: ...

    @abstractmethod
    async def list_all(self, *, offset: int = 0, limit: int = 20) -> list[OrganizationEntity]: ...

    @abstractmethod
    async def save(self, org: OrganizationEntity) -> OrganizationEntity: ...

    @abstractmethod
    async def delete(self, org_id: uuid.UUID) -> None: ...
