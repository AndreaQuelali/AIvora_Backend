"""Organization ORM model."""

from __future__ import annotations

import uuid

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class OrganizationModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """SQLAlchemy ORM model for the ``organizations`` table."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="free")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="trial")
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_documents: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Relationships
    members: Mapped[list["UserModel"]] = relationship(  # noqa: F821
        "UserModel", back_populates="organization", lazy="select"
    )
    roles: Mapped[list["RoleModel"]] = relationship(  # noqa: F821
        "RoleModel", back_populates="organization", lazy="select"
    )
    documents: Mapped[list["DocumentModel"]] = relationship(  # noqa: F821
        "DocumentModel", back_populates="organization", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<OrganizationModel id={self.id} slug={self.slug!r}>"
