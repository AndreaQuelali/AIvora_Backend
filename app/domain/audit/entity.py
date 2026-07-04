"""Audit Log domain entity — immutable record of system events."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.base import Entity, IRepository


class AuditAction(StrEnum):
    """Auditable action types."""

    # Auth
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_REFRESHED = "auth.token_refreshed"

    # Users
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_ROLE_ASSIGNED = "user.role_assigned"

    # Organizations
    ORG_CREATED = "organization.created"
    ORG_UPDATED = "organization.updated"
    ORG_PLAN_CHANGED = "organization.plan_changed"

    # Documents
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_DELETED = "document.deleted"

    # API Keys
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"

    # Admin
    ADMIN_ACTION = "admin.action"


@dataclass
class AuditLogEntity(Entity):
    """Immutable audit log record.

    Audit logs are never updated or deleted — only appended.

    Attributes:
        action: Type of action performed.
        actor_id: User/API key that triggered the action.
        actor_type: 'user' or 'api_key'.
        organization_id: Tenant context.
        resource_type: Type of resource affected.
        resource_id: ID of the affected resource.
        ip_address: Client IP address.
        user_agent: Client user agent.
        metadata: Arbitrary extra data (before/after state, etc.).
        success: Whether the action succeeded.
        error_message: Failure reason if not successful.
    """

    action: AuditAction = AuditAction.ADMIN_ACTION
    actor_id: uuid.UUID | None = None
    actor_type: str = "user"
    organization_id: uuid.UUID | None = None
    resource_type: str = ""
    resource_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None


class IAuditRepository(IRepository[AuditLogEntity]):
    """Abstract audit log repository — append-only."""

    @abstractmethod
    async def append(self, log: AuditLogEntity) -> AuditLogEntity: ...

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        actor_id: uuid.UUID | None = None,
        action: AuditAction | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[AuditLogEntity]: ...
