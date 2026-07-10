"""Document processing tasks — async pipeline triggered after upload."""

from __future__ import annotations

from app.infrastructure.messaging.celery_app import celery_app


@celery_app.task(
    name="app.tasks.document_tasks.process_document",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="documents",
)
def process_document_task(self: object, document_id: str) -> dict[str, str]:
    """Process an uploaded document: extract text, chunk, embed, index.

    TODO: Implement when RAG pipeline is ready:
    1. Load file from storage
    2. Extract text (PDF/DOCX/etc.)
    3. Chunk text with overlap
    4. Generate embeddings via AI provider
    5. Index chunks into Elasticsearch
    6. Update document status in DB

    Args:
        document_id: UUID string of the document to process.
    """
    # Placeholder — will be implemented with RAG pipeline
    return {"status": "queued", "document_id": document_id}
