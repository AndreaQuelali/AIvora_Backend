"""Document aggregate — entity, value objects, domain events, repository interface."""

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
class FileSize(ValueObject):
    """File size in bytes."""

    bytes: int

    @property
    def mb(self) -> float:
        return self.bytes / (1024 * 1024)


@dataclass(frozen=True)
class StoragePath(ValueObject):
    """Relative path to the stored file within the configured backend."""

    value: str

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DocumentStatus(StrEnum):
    """Document processing lifecycle status."""

    PENDING = "pending"          # Uploaded, awaiting processing
    PROCESSING = "processing"    # Celery worker is processing
    INDEXED = "indexed"          # In Elasticsearch, ready for RAG
    FAILED = "failed"            # Processing failed
    ARCHIVED = "archived"        # Soft-archived, not searchable


class DocumentType(StrEnum):
    """Supported document MIME type groups."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    XLSX = "xlsx"
    PPTX = "pptx"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Domain Events
# ---------------------------------------------------------------------------


@dataclass
class DocumentUploadedEvent(DomainEvent):
    """Raised when a user successfully uploads a document."""

    document_id: uuid.UUID = field(default_factory=uuid.uuid4)
    organization_id: uuid.UUID | None = None
    uploader_id: uuid.UUID | None = None


@dataclass
class DocumentIndexedEvent(DomainEvent):
    """Raised when a document has been indexed in Elasticsearch."""

    document_id: uuid.UUID = field(default_factory=uuid.uuid4)
    chunk_count: int = 0


@dataclass
class DocumentProcessingFailedEvent(DomainEvent):
    """Raised when document processing fails."""

    document_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str = ""


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------


@dataclass
class DocumentEntity(AggregateRoot):
    """Document aggregate root.

    Attributes:
        organization_id: Owning organization (tenant isolation).
        uploader_id: User who uploaded the document.
        title: Document title (derived from filename or user-provided).
        filename: Original filename.
        document_type: Detected document type.
        mime_type: MIME type string.
        file_size: File size in bytes.
        storage_path: Path in the configured storage backend.
        status: Current processing status.
        page_count: Number of pages (filled after processing).
        chunk_count: Number of indexed chunks (filled after indexing).
        elasticsearch_index: ES index name where document chunks are stored.
        error_message: Last error message if status is FAILED.
    """

    organization_id: uuid.UUID | None = None
    uploader_id: uuid.UUID | None = None
    title: str = ""
    filename: str = ""
    document_type: DocumentType = DocumentType.UNKNOWN
    mime_type: str = ""
    file_size: FileSize = field(default_factory=lambda: FileSize(0))
    storage_path: StoragePath = field(default_factory=lambda: StoragePath(""))
    status: DocumentStatus = DocumentStatus.PENDING
    page_count: int | None = None
    chunk_count: int | None = None
    elasticsearch_index: str | None = None
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        organization_id: uuid.UUID,
        uploader_id: uuid.UUID | None,
        title: str,
        filename: str,
        mime_type: str,
        file_size: FileSize,
        storage_path: StoragePath,
    ) -> DocumentEntity:
        """Create a new document, tracking initial state and dispatching upload event."""
        # Infers type from extension
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        doc_type = DocumentType.UNKNOWN
        if ext in ("pdf", "docx", "txt", "md", "html", "xlsx", "pptx"):
            doc_type = DocumentType(ext)

        doc = cls(
            organization_id=organization_id,
            uploader_id=uploader_id,
            title=title,
            filename=filename,
            document_type=doc_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            status=DocumentStatus.PENDING,
        )
        doc.record_event(
            DocumentUploadedEvent(
                document_id=doc.id,
                organization_id=organization_id,
                uploader_id=uploader_id,
            )
        )
        return doc

    def mark_processing(self) -> None:

        """Transition to PROCESSING status."""
        self.status = DocumentStatus.PROCESSING
        self.touch()

    def mark_indexed(self, chunk_count: int, index_name: str) -> None:
        """Transition to INDEXED after successful chunking and indexing."""
        self.status = DocumentStatus.INDEXED
        self.chunk_count = chunk_count
        self.elasticsearch_index = index_name
        self.touch()
        self.record_event(
            DocumentIndexedEvent(document_id=self.id, chunk_count=chunk_count)
        )

    def mark_failed(self, reason: str) -> None:
        """Transition to FAILED with an error message."""
        self.status = DocumentStatus.FAILED
        self.error_message = reason
        self.touch()
        self.record_event(
            DocumentProcessingFailedEvent(document_id=self.id, reason=reason)
        )

    def archive(self) -> None:
        """Soft-archive the document."""
        self.status = DocumentStatus.ARCHIVED
        self.touch()


# ---------------------------------------------------------------------------
# Repository Interface
# ---------------------------------------------------------------------------


class IDocumentRepository(IRepository[DocumentEntity]):
    """Abstract document repository."""

    @abstractmethod
    async def get_by_id(self, document_id: uuid.UUID) -> DocumentEntity | None: ...

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        status: DocumentStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[DocumentEntity]: ...

    @abstractmethod
    async def save(self, document: DocumentEntity) -> DocumentEntity: ...

    @abstractmethod
    async def delete(self, document_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def count_by_organization(self, organization_id: uuid.UUID) -> int: ...
