"""Shared domain primitives — base entity, value object, and domain event types.

Rules:
- No imports from infrastructure, services, or FastAPI.
- All IDs use UUID for global uniqueness.
- Entities are mutable; Value Objects are frozen.
"""

from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def new_uuid() -> uuid.UUID:
    """Generate a new UUID v4."""
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# Base Entity
# ---------------------------------------------------------------------------


@dataclass
class Entity:
    """Base class for all domain entities.

    An entity has identity (ID) and is mutable over time.
    Equality is determined by ``id`` alone, not attribute values.
    """

    id: uuid.UUID = field(default_factory=new_uuid)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def touch(self) -> None:
        """Update ``updated_at`` to the current UTC time."""
        self.updated_at = utcnow()


# ---------------------------------------------------------------------------
# Base Value Object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValueObject:
    """Base class for value objects.

    Value objects are immutable and compared by their attribute values.
    """


# ---------------------------------------------------------------------------
# Domain Events
# ---------------------------------------------------------------------------


@dataclass
class DomainEvent:
    """Base class for domain events.

    Domain events represent something that happened in the domain.
    They are recorded by aggregates and published to handlers.
    """

    event_id: uuid.UUID = field(default_factory=new_uuid)
    occurred_at: datetime = field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class AggregateRoot(Entity):
    """Base class for aggregate roots.

    Aggregate roots maintain a list of uncommitted domain events.
    Events are cleared after being published.
    """

    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event to be published."""
        self._events.append(event)

    def pop_events(self) -> list[DomainEvent]:
        """Return and clear all recorded domain events."""
        events = list(self._events)
        self._events.clear()
        return events


# ---------------------------------------------------------------------------
# Repository Interface
# ---------------------------------------------------------------------------


class IRepository[T](ABC):
    """Generic repository interface.

    Implementations live in the infrastructure layer (SQLAlchemy).
    The domain only knows about this abstract interface.
    """
