"""User ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin


class UserModel(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy ORM model for the ``users`` table."""

    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_verification"
    )
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped["OrganizationModel | None"] = relationship(  # noqa: F821
        "OrganizationModel", back_populates="members", lazy="select"
    )
    roles: Mapped[list["RoleModel"]] = relationship(  # noqa: F821
        "RoleModel",
        secondary="user_roles",
        back_populates="users",
        lazy="select",
    )
    api_keys: Mapped[list["ApiKeyModel"]] = relationship(  # noqa: F821
        "ApiKeyModel", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    documents: Mapped[list["DocumentModel"]] = relationship(  # noqa: F821
        "DocumentModel", back_populates="uploader", lazy="select"
    )
    conversations: Mapped[list["ConversationModel"]] = relationship(  # noqa: F821
        "ConversationModel", back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email!r}>"
