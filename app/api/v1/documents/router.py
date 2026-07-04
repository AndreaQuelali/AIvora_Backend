"""Documents router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.auth import get_current_user_id
from app.dependencies.pagination import PaginationParams, get_pagination
from app.dependencies.services import get_document_service, get_user_repository, get_document_repository
from app.exceptions.base import UnauthorizedError, ForbiddenError
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.repositories.user_repository import UserRepository
from app.repositories.document_repository import DocumentRepository

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=StandardResponse[DocumentUploadResponse], status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
    doc_service: DocumentService = Depends(get_document_service),
) -> StandardResponse[DocumentUploadResponse]:
    """Upload a document. Processing is handled asynchronously by Celery."""
    user = await user_repo.get_by_id(current_user_id)
    if not user or not user.organization_id:
        raise ForbiddenError("User must belong to an organization to upload documents.")

    content = await file.read()
    res = await doc_service.upload_and_queue_document(
        filename=file.filename or "uploaded_file",
        content_type=file.content_type or "application/octet-stream",
        file_bytes=content,
        uploader_id=current_user_id,
        organization_id=user.organization_id,
    )
    return StandardResponse(data=res)


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
    doc_repo: DocumentRepository = Depends(get_document_repository),
) -> PaginatedResponse[DocumentResponse]:
    """List all documents in the organization."""
    user = await user_repo.get_by_id(current_user_id)
    if not user or not user.organization_id:
        raise ForbiddenError("User is not associated with any organization.")

    docs = await doc_repo.list_by_organization(
        user.organization_id,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    # Count total
    total = await doc_repo.count_by_organization(user.organization_id)
    
    return PaginatedResponse.create(
        data=[DocumentResponse.model_validate(d) for d in docs],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )



@router.get("/{document_id}", response_model=StandardResponse[DocumentResponse])
async def get_document(
    document_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    doc_service: DocumentService = Depends(get_document_service),
) -> StandardResponse[DocumentResponse]:
    """Get document metadata by ID."""
    doc = await doc_service.get_document_by_id(document_id)
    return StandardResponse(data=doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
) -> None:
    """Delete a document and its indexed chunks."""
    await doc_repo.delete(document_id)

