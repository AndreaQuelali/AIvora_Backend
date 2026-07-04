"""Elasticsearch async client placeholder.

All methods are stubs that will be implemented when the RAG pipeline is added.
The interface is defined here so that the service and application layers
can depend on it without changes when the implementation arrives.
"""

from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_es_client: Any = None  # elasticsearch.AsyncElasticsearch


async def get_elasticsearch_client() -> Any:
    """Return the module-level Elasticsearch client."""
    global _es_client
    if _es_client is None:
        from elasticsearch import AsyncElasticsearch

        settings = get_settings()
        kwargs: dict[str, Any] = {"hosts": settings.elasticsearch.hosts}
        if settings.elasticsearch.username and settings.elasticsearch.password:
            kwargs["basic_auth"] = (
                settings.elasticsearch.username,
                settings.elasticsearch.password,
            )
        _es_client = AsyncElasticsearch(**kwargs)
    return _es_client


class ElasticsearchClient:
    """Async Elasticsearch client wrapper.

    All methods are stubs to be implemented with the RAG pipeline.
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    async def ping(self) -> bool:
        """Check if Elasticsearch is reachable."""
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def index_document(
        self,
        index: str,
        document_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Index a document chunk. To be implemented with chunking pipeline."""
        raise NotImplementedError("Elasticsearch indexing not yet implemented.")

    async def search(
        self,
        index: str,
        query: dict[str, Any],
        *,
        size: int = 10,
    ) -> dict[str, Any]:
        """Full-text and vector search. To be implemented with RAG pipeline."""
        raise NotImplementedError("Elasticsearch search not yet implemented.")

    async def delete_document(self, index: str, document_id: str) -> None:
        """Delete a document chunk by ID."""
        raise NotImplementedError("Elasticsearch delete not yet implemented.")

    async def create_index(self, index: str, mappings: dict[str, Any]) -> None:
        """Create an index with given mappings (called during setup)."""
        raise NotImplementedError("Elasticsearch index creation not yet implemented.")
