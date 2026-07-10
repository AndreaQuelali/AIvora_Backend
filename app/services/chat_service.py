"""Chat service — coordinates RAG conversations, messages, and AI completions."""

from __future__ import annotations

import uuid

from app.domain.conversation.entity import ConversationEntity, MessageEntity, MessageRole
from app.exceptions.base import NotFoundError
from app.infrastructure.ai.base import IAIProvider
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.schemas.conversation import ConversationResponse, MessageResponse


class ChatService:
    """Manages conversations and triggers vector search and LLM context generation."""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        ai_provider: IAIProvider,
    ) -> None:
        self._conversation_repo = conversation_repo
        self._message_repo = message_repo
        self._ai_provider = ai_provider

    async def create_new_conversation(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
    ) -> ConversationResponse:
        """Create a new empty conversation."""
        entity = ConversationEntity.initiate(
            organization_id=organization_id,
            user_id=user_id,
            title=title,
        )
        await self._conversation_repo.save(entity)
        return ConversationResponse.model_validate(entity)

    async def get_conversation_by_id(self, conversation_id: uuid.UUID) -> ConversationResponse:
        """Fetch conversation by primary key."""
        conv = await self._conversation_repo.get_by_id(conversation_id)
        if not conv:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found.")
        return ConversationResponse.model_validate(conv)

    async def send_new_message(
        self,
        conversation_id: uuid.UUID,
        user_content: str,
    ) -> MessageResponse:
        """Add user message, trigger AI completions, and append the assistant message.

        This acts as the coordinator for the RAG pipeline when running chat.
        """
        conversation = await self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError(f"Conversation with ID {conversation_id} not found.")

        # 1. Save User Message
        user_message = MessageEntity.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_content,
        )
        # Count tokens (async helper)
        user_message.token_count = await self._ai_provider.count_tokens(user_content)
        await self._message_repo.save(user_message)

        # 2. TODO: Retrieve relevant context chunk nodes from Elasticsearch search results
        # contextual_chunks = await self._search_client.search(...)
        # system_prompt = "Use the following context to answer: ..."

        # 3. Generate Assistant completion
        # Placeholder messages list format
        chat_history = [
            {"role": "user", "content": user_content},
        ]
        completion = await self._ai_provider.generate(chat_history)

        # 4. Save Assistant Message
        assistant_message = MessageEntity.create(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=completion,
        )
        assistant_message.token_count = await self._ai_provider.count_tokens(completion)
        await self._message_repo.save(assistant_message)

        return MessageResponse.model_validate(assistant_message)
