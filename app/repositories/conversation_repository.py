"""Concrete conversation and message repositories implementation using SQLAlchemy 2.0 async."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.conversation.entity import (
    ConversationEntity,
    IConversationRepository,
    IMessageRepository,
    MessageEntity,
)
from app.infrastructure.models.conversation import ConversationModel, MessageModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import DataMapper


class ConversationRepository(BaseRepository[ConversationModel], IConversationRepository):
    """SQLAlchemy implementation of the IConversationRepository interface."""

    model = ConversationModel

    async def get_by_id(self, conversation_id: uuid.UUID) -> ConversationEntity | None:
        stmt = (
            select(ConversationModel)
            .where(
                ConversationModel.id == conversation_id,
                ConversationModel.deleted_at.is_(None),
            )
            .options(selectinload(ConversationModel.messages))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataMapper.conv_to_entity(model) if model else None

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ConversationEntity]:
        stmt = (
            select(ConversationModel)
            .where(
                ConversationModel.user_id == user_id,
                ConversationModel.deleted_at.is_(None),
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [DataMapper.conv_to_entity(m) for m in result.scalars().all()]

    async def save(self, conversation: ConversationEntity) -> ConversationEntity:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.conv_to_model(conversation)
            existing_model.title = model.title
            existing_model.status = model.status
            existing_model.updated_at = conversation.updated_at
            await self._session.flush()
            return conversation
        else:
            model = DataMapper.conv_to_model(conversation)
            await self.create(model)
            return conversation

    async def delete(self, conversation_id: uuid.UUID) -> None:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            from app.domain.base import utcnow
            model.deleted_at = utcnow()
            await self._session.flush()


class MessageRepository(BaseRepository[MessageModel], IMessageRepository):
    """SQLAlchemy implementation of the IMessageRepository interface."""

    model = MessageModel

    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[MessageEntity]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [DataMapper.message_to_entity(m) for m in result.scalars().all()]

    async def save(self, message: MessageEntity) -> MessageEntity:
        stmt = select(MessageModel).where(MessageModel.id == message.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataMapper.message_to_model(message)
            existing_model.content = model.content
            existing_model.token_count = model.token_count
            existing_model.model = model.model
            existing_model.updated_at = message.updated_at
            await self._session.flush()
            return message
        else:
            model = DataMapper.message_to_model(message)
            await self.create(model)
            return message
