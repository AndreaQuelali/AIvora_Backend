"""Document schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    filename: str
    document_type: str
    mime_type: str
    file_size_bytes: int
    status: str
    page_count: int | None
    chunk_count: int | None
    organization_id: uuid.UUID
    uploader_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    message: str
