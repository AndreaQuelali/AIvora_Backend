"""Search router — full-text and semantic document search."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    document_ids: list[uuid.UUID] | None = None
    top_k: int = 5


class SearchResultItem(BaseModel):
    document_id: uuid.UUID
    document_title: str
    chunk_text: str
    score: float
    page: int | None = None


@router.post("", response_model=list[SearchResultItem])
async def semantic_search(
    body: SearchRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[SearchResultItem]:
    """Perform semantic/hybrid search over indexed documents."""
    raise NotImplementedError("Elasticsearch search not yet implemented.")
