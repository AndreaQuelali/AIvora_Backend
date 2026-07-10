"""Conversation and Message aggregates."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.base import AggregateRoot, Entity, IRepository


class MessageRole(StrEnum):
    """Who sent the message in a conversation turn."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class MessageEntity(Entity):
    """A single turn in a chat conversation.

    Attributes:
        conversation_id: Parent conversation.
        role: Who produced this message.
        content: Raw text content.
        token_count: Approximate tokens used (filled by AI provider).
        source_document_ids: Documents referenced in this response (RAG).
        model: AI model used to generate the response.
    """

    conversation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: MessageRole = MessageRole.USER
    content: str = ""
    token_count: int | None = None
    source_document_ids: list[uuid.UUID] = field(default_factory=list)
    model: str | None = None

    @classmethod
    def create(
        cls,
        conversation_id: uuid.UUID,
        role: MessageRole,
        content: str,
        token_count: int | None = None,
        model: str | None = None,
    ) -> MessageEntity:
        """Create a new message turn."""
        return cls(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            model=model,
        )


@dataclass
class ConversationEntity(AggregateRoot):
    """Conversation aggregate root — a RAG chat session.

    Attributes:
        organization_id: Tenant scoping.
        user_id: Owning user.
        title: Auto-generated or user-set title.
        status: Lifecycle status.
        messages: Ordered list of messages (lazy-loaded in repo).
        document_ids: Documents in scope for this conversation.
    """

    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    title: str = "New Conversation"
    status: ConversationStatus = ConversationStatus.ACTIVE
    messages: list[MessageEntity] = field(default_factory=list)
    document_ids: list[uuid.UUID] = field(default_factory=list)

    @classmethod
    def initiate(
        cls,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = "New Conversation",
    ) -> ConversationEntity:
        """Initiate a new conversation session."""
        return cls(
            organization_id=organization_id,
            user_id=user_id,
            title=title,
            status=ConversationStatus.ACTIVE,
        )

    def add_message(self, message: MessageEntity) -> None:
        """Append a message to this conversation."""
        self.messages.append(message)
        self.touch()

    def archive(self) -> None:
        """Archive the conversation."""
        self.status = ConversationStatus.ARCHIVED
        self.touch()

    def set_title(self, title: str) -> None:
        """Update the conversation title."""
        self.title = title
        self.touch()


class IConversationRepository(IRepository[ConversationEntity]):
    """Abstract conversation repository."""

    @abstractmethod
    async def get_by_id(self, conversation_id: uuid.UUID) -> ConversationEntity | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> list[ConversationEntity]: ...

    @abstractmethod
    async def save(self, conversation: ConversationEntity) -> ConversationEntity: ...

    @abstractmethod
    async def delete(self, conversation_id: uuid.UUID) -> None: ...


class IMessageRepository(IRepository[MessageEntity]):
    """Abstract message repository."""

    @abstractmethod
    async def list_by_conversation(
        self, conversation_id: uuid.UUID, *, offset: int = 0, limit: int = 50
    ) -> list[MessageEntity]: ...

    @abstractmethod
    async def save(self, message: MessageEntity) -> MessageEntity: ...
