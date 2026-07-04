"""Chat router — conversations and messages."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_id
from app.dependencies.pagination import PaginationParams, get_pagination
from app.dependencies.services import (
    get_chat_service,
    get_user_repository,
    get_conversation_repository,
    get_message_repository,
)
from app.exceptions.base import ForbiddenError
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.chat_service import ChatService
from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository, MessageRepository

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/conversations", response_model=StandardResponse[ConversationResponse], status_code=201)
async def create_conversation(
    body: ConversationCreateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
    chat_service: ChatService = Depends(get_chat_service),
) -> StandardResponse[ConversationResponse]:
    """Start a new RAG conversation."""
    user = await user_repo.get_by_id(current_user_id)
    if not user or not user.organization_id:
        raise ForbiddenError("User is not associated with an organization.")

    title = body.title or "New Conversation"
    conv = await chat_service.create_new_conversation(
        organization_id=user.organization_id,
        user_id=current_user_id,
        title=title,
    )
    return StandardResponse(data=conv)


@router.get("/conversations", response_model=PaginatedResponse[ConversationResponse])
async def list_conversations(
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    conv_repo: ConversationRepository = Depends(get_conversation_repository),
) -> PaginatedResponse[ConversationResponse]:
    """List the user's conversations."""
    convs = await conv_repo.list_by_user(
        current_user_id,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    # Since list_by_user returns Conversations, we can count user's conversations:
    total = await conv_repo.count(filters={"user_id": current_user_id, "deleted_at": None})
    return PaginatedResponse.create(
        data=[ConversationResponse.model_validate(c) for c in convs],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/conversations/{conversation_id}", response_model=StandardResponse[ConversationResponse])
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> StandardResponse[ConversationResponse]:
    """Get a conversation by ID."""
    conv = await chat_service.get_conversation_by_id(conversation_id)
    return StandardResponse(data=conv)


@router.post("/conversations/{conversation_id}/messages", response_model=StandardResponse[MessageResponse], status_code=201)
async def send_message(
    conversation_id: uuid.UUID,
    body: MessageCreateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> StandardResponse[MessageResponse]:
    """Send a message and get an AI-powered response."""
    msg = await chat_service.send_new_message(conversation_id, body.content)
    return StandardResponse(data=msg)


@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedResponse[MessageResponse])
async def list_messages(
    conversation_id: uuid.UUID,
    pagination: PaginationParams = Depends(get_pagination),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    message_repo: MessageRepository = Depends(get_message_repository),
) -> PaginatedResponse[MessageResponse]:
    """List messages in a conversation."""
    messages = await message_repo.list_by_conversation(
        conversation_id,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    total = await message_repo.count(filters={"conversation_id": conversation_id})
    return PaginatedResponse.create(
        data=[MessageResponse.model_validate(m) for m in messages],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )

