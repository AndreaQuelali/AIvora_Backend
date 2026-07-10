"""Concrete document repository implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.domain.document.entity import DocumentEntity, DocumentStatus, IDocumentRepository
from app.infrastructure.models.document import DocumentModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class DocumentRepository(BaseRepository[DocumentModel], IDocumentRepository):
    """SQLAlchemy implementation of the IDocumentRepository interface."""

    model = DocumentModel

    async def get_by_id(self, document_id: uuid.UUID) -> DocumentEntity | None:  # type: ignore[override]
        stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.doc_to_entity(model) if model else None

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        status: DocumentStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[DocumentEntity]:
        stmt = select(DocumentModel).where(
            DocumentModel.organization_id == organization_id,
            DocumentModel.deleted_at.is_(None),
        )
        if status:
            stmt = stmt.where(DocumentModel.status == status.value)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [DataMapper.doc_to_entity(m) for m in result.scalars().all()]

    async def save(self, document: DocumentEntity) -> DocumentEntity:
        stmt = select(DocumentModel).where(DocumentModel.id == document.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.doc_to_model(document)
            for attr in (
                "title",
                "filename",
                "document_type",
                "mime_type",
                "file_size_bytes",
                "storage_path",
                "status",
                "page_count",
                "chunk_count",
                "elasticsearch_index",
                "error_message",
            ):
                setattr(existing_model, attr, getattr(model, attr))
            existing_model.updated_at = document.updated_at
            await self._session.flush()
            return document
        else:
            model = DataMapper.doc_to_model(document)
            await self.create(model)
            return document

    async def delete(self, document_id: uuid.UUID) -> None:  # type: ignore[override]
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            from app.domain.base import utcnow

            model.deleted_at = utcnow()
            await self._session.flush()

    async def count_by_organization(self, organization_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(DocumentModel)
            .where(
                DocumentModel.organization_id == organization_id,
                DocumentModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
