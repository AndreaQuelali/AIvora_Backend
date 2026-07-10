"""Role and Permission domain entities."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass, field

from app.domain.base import AggregateRoot, Entity, IRepository

# ---------------------------------------------------------------------------
# Permission Entity
# ---------------------------------------------------------------------------


@dataclass
class PermissionEntity(Entity):
    """A granular permission (e.g., 'documents:read', 'admin:users:delete').

    Permissions follow the pattern: ``resource:action`` or
    ``resource:sub-resource:action``.
    """

    name: str = ""
    description: str = ""
    resource: str = ""
    action: str = ""

    @property
    def code(self) -> str:
        """Colon-separated permission code."""
        return f"{self.resource}:{self.action}"


# ---------------------------------------------------------------------------
# Role Entity
# ---------------------------------------------------------------------------


@dataclass
class RoleEntity(AggregateRoot):
    """Role aggregate root — groups a set of permissions.

    Attributes:
        name: Human-readable role name (e.g., 'Admin', 'Viewer').
        description: Explanation of what this role grants.
        organization_id: None for system-wide roles; scoped otherwise.
        permission_ids: Set of granted permission IDs.
        is_system: System roles cannot be deleted.
    """

    name: str = ""
    description: str = ""
    organization_id: uuid.UUID | None = None
    permission_ids: set[uuid.UUID] = field(default_factory=set)
    is_system: bool = False

    # -- Predefined system role names (used as constants across the app)
    SUPER_ADMIN: str = "super_admin"
    ADMIN: str = "admin"
    MEMBER: str = "member"
    VIEWER: str = "viewer"

    def grant_permission(self, permission_id: uuid.UUID) -> None:
        """Add a permission to this role."""
        self.permission_ids.add(permission_id)
        self.touch()

    def revoke_permission(self, permission_id: uuid.UUID) -> None:
        """Remove a permission from this role."""
        self.permission_ids.discard(permission_id)
        self.touch()

    def has_permission(self, permission_id: uuid.UUID) -> bool:
        """Check if the role includes a given permission."""
        return permission_id in self.permission_ids


# ---------------------------------------------------------------------------
# Repository Interfaces
# ---------------------------------------------------------------------------


class IRoleRepository(IRepository[RoleEntity]):
    """Abstract role repository."""

    @abstractmethod
    async def get_by_id(self, role_id: uuid.UUID) -> RoleEntity | None: ...

    @abstractmethod
    async def get_by_name(
        self, name: str, *, organization_id: uuid.UUID | None = None
    ) -> RoleEntity | None: ...

    @abstractmethod
    async def list_all(self, *, organization_id: uuid.UUID | None = None) -> list[RoleEntity]: ...

    @abstractmethod
    async def save(self, role: RoleEntity) -> RoleEntity: ...

    @abstractmethod
    async def delete(self, role_id: uuid.UUID) -> None: ...


class IPermissionRepository(IRepository[PermissionEntity]):
    """Abstract permission repository."""

    @abstractmethod
    async def get_by_id(self, perm_id: uuid.UUID) -> PermissionEntity | None: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> PermissionEntity | None: ...

    @abstractmethod
    async def list_all(self) -> list[PermissionEntity]: ...

    @abstractmethod
    async def save(self, permission: PermissionEntity) -> PermissionEntity: ...
