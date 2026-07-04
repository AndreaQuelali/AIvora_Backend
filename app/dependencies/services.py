"""FastAPI Dependency Injection providers for application services."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.infrastructure.ai.base import IAIProvider, NoOpAIProvider
from app.infrastructure.storage.base import IFileStorage, LocalFileStorage
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.user_service import UserService


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_document_repository(session: AsyncSession = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(session)


def get_conversation_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRepository:
    return ConversationRepository(session)


def get_message_repository(session: AsyncSession = Depends(get_db_session)) -> MessageRepository:
    return MessageRepository(session)


# --- Infrastructure singletons ---
def get_file_storage() -> IFileStorage:
    # Use LocalFileStorage for development, could swap with S3/GCS here
    return LocalFileStorage()


def get_ai_provider() -> IAIProvider:
    return NoOpAIProvider()


# --- Application Services injection points ---
def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)


def get_document_service(
    repo: DocumentRepository = Depends(get_document_repository),
    storage: IFileStorage = Depends(get_file_storage),
) -> DocumentService:
    return DocumentService(repo, storage)


def get_chat_service(
    conversation_repo: ConversationRepository = Depends(get_conversation_repository),
    message_repo: MessageRepository = Depends(get_message_repository),
    ai_provider: IAIProvider = Depends(get_ai_provider),
) -> ChatService:
    return ChatService(conversation_repo, message_repo, ai_provider)
