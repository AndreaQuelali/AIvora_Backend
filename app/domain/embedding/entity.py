"""Embedding domain placeholder — future RAG infrastructure.

This module defines the interface that the embedding/vector-storage layer
will implement. No ML logic belongs here — only domain contract definitions.
"""

from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass, field

from app.domain.base import Entity, IRepository


@dataclass
class EmbeddingEntity(Entity):
    """Vector embedding for a document chunk.

    Attributes:
        document_id: Parent document.
        organization_id: Tenant scoping.
        chunk_index: Position within the document.
        chunk_text: Raw text of this chunk.
        vector: Float array from the embedding model (empty until RAG impl).
        model: Embedding model name used to generate the vector.
        token_count: Token count for this chunk.
        elasticsearch_doc_id: ID in the Elasticsearch index.
    """

    document_id: uuid.UUID = field(default_factory=uuid.uuid4)
    organization_id: uuid.UUID | None = None
    chunk_index: int = 0
    chunk_text: str = ""
    vector: list[float] = field(default_factory=list)
    model: str = ""
    token_count: int = 0
    elasticsearch_doc_id: str | None = None


class IEmbeddingRepository(IRepository[EmbeddingEntity]):
    """Abstract embedding repository — to be implemented with Elasticsearch kNN."""

    @abstractmethod
    async def upsert(self, embedding: EmbeddingEntity) -> EmbeddingEntity: ...

    @abstractmethod
    async def list_by_document(self, document_id: uuid.UUID) -> list[EmbeddingEntity]: ...

    @abstractmethod
    async def similarity_search(
        self,
        query_vector: list[float],
        organization_id: uuid.UUID,
        *,
        top_k: int = 5,
        document_ids: list[uuid.UUID] | None = None,
    ) -> list[EmbeddingEntity]: ...

    @abstractmethod
    async def delete_by_document(self, document_id: uuid.UUID) -> None: ...
