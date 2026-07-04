"""Role, Permission, and join-table ORM models."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin

# ---------------------------------------------------------------------------
# Association tables (M:N)
# ---------------------------------------------------------------------------

UserRoleModel = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

RolePermissionModel = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Permission
# ---------------------------------------------------------------------------


class PermissionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)

    roles: Mapped[list["RoleModel"]] = relationship(
        "RoleModel", secondary="role_permissions", back_populates="permissions", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<PermissionModel {self.resource}:{self.action}>"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------


class RoleModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    organization: Mapped["OrganizationModel | None"] = relationship(  # noqa: F821
        "OrganizationModel", back_populates="roles", lazy="select"
    )
    users: Mapped[list["UserModel"]] = relationship(  # noqa: F821
        "UserModel", secondary="user_roles", back_populates="roles", lazy="select"
    )
    permissions: Mapped[list[PermissionModel]] = relationship(
        "PermissionModel", secondary="role_permissions", back_populates="roles", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<RoleModel name={self.name!r}>"
