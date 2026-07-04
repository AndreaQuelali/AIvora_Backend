"""Document service — coordinates document uploads, storage, and processing tasks."""

from __future__ import annotations

import uuid
from typing import Any

from app.domain.document.entity import DocumentEntity, DocumentStatus, FileSize, StoragePath
from app.exceptions.base import NotFoundError
from app.infrastructure.storage.base import IFileStorage
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.tasks.document_tasks import process_document_task


class DocumentService:
    """Coordinates file system storage, PostgreSQL database metadata, and Celery processing."""

    def __init__(self, document_repo: DocumentRepository, storage: IFileStorage) -> None:
        self._document_repo = document_repo
        self._storage = storage

    async def get_document_by_id(self, document_id: uuid.UUID) -> DocumentResponse:
        """Fetch document by primary key."""
        doc = await self._document_repo.get_by_id(document_id)
        if not doc:
            raise NotFoundError(f"Document with ID {document_id} not found.")
        return DocumentResponse.model_validate(doc)

    async def upload_and_queue_document(
        self,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        uploader_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> DocumentUploadResponse:
        """Process file uploads by storing content, creating record, and dispatching Celery pipeline."""
        # 1. Generate unique file storage path
        file_extension = filename.split(".")[-1] if "." in filename else "bin"
        unique_id = uuid.uuid4()
        storage_filename = f"{unique_id}.{file_extension}"
        storage_path = f"org_{organization_id}/docs/{storage_filename}"

        # 2. Persist to static file storage (local/S3/GCS)
        await self._storage.upload(
            file_bytes=file_bytes,
            destination_path=storage_path,
            content_type=content_type,
        )

        # 3. Create domain entity in pending state
        entity = DocumentEntity.create(
            organization_id=organization_id,
            uploader_id=uploader_id,
            title=filename,
            filename=filename,
            mime_type=content_type,
            file_size=FileSize(len(file_bytes)),
            storage_path=StoragePath(storage_path),
        )
        await self._document_repo.save(entity)

        # 4. Trigger background extraction task asynchronously via Celery
        # We pass str(entity.id) to the task runner
        process_document_task.delay(str(entity.id))

        return DocumentUploadResponse(
            id=entity.id,
            filename=entity.filename,
            status=entity.status.value,
            message="Document uploaded successfully and queued for AI indexing.",
        )
