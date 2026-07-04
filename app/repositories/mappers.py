"""Mappers between pure domain entities (Domain layer) and SQLAlchemy ORM models (Infrastructure layer).

Enforces strict separation of concerns, keeping the Domain layer completely
independent of SQLAlchemy and database schemas.
"""

from __future__ import annotations

import uuid
from app.domain.user.entity import UserEntity, Email, HashedPassword, UserStatus
from app.domain.organization.entity import OrganizationEntity, Slug, OrganizationPlan, OrganizationStatus
from app.domain.document.entity import DocumentEntity, FileSize, StoragePath, DocumentType, DocumentStatus
from app.domain.conversation.entity import ConversationEntity, MessageEntity, ConversationStatus, MessageRole
from app.domain.api_key.entity import ApiKeyEntity
from app.domain.audit.entity import AuditLogEntity, AuditAction
from app.domain.role.entity import PermissionEntity, RoleEntity

from app.infrastructure.models.user import UserModel
from app.infrastructure.models.organization import OrganizationModel
from app.infrastructure.models.document import DocumentModel
from app.infrastructure.models.conversation import ConversationModel, MessageModel
from app.infrastructure.models.api_key import ApiKeyModel
from app.infrastructure.models.audit_log import AuditLogModel
from app.infrastructure.models.role import RoleModel, PermissionModel



class DataMapper:
    """Static mapping methods for domain entities and database models."""

    # -----------------------------------------------------------------------
    # User Mapper
    # -----------------------------------------------------------------------
    @staticmethod
    def user_to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            email=Email(model.email),
            hashed_password=HashedPassword(model.hashed_password),
            full_name=model.full_name,
            organization_id=model.organization_id,
            role_ids={role.id for role in model.roles},
            status=UserStatus(model.status),
            is_superuser=model.is_superuser,
        )

    @staticmethod
    def user_to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            email=str(entity.email),
            hashed_password=entity.hashed_password.value,
            full_name=entity.full_name,
            organization_id=entity.organization_id,
            status=entity.status.value,
            is_superuser=entity.is_superuser,
        )

    # -----------------------------------------------------------------------
    # Organization Mapper
    # -----------------------------------------------------------------------
    @staticmethod
    def org_to_entity(model: OrganizationModel) -> OrganizationEntity:
        return OrganizationEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            slug=Slug(model.slug),
            plan=OrganizationPlan(model.plan),
            status=OrganizationStatus(model.status),
            owner_id=model.owner_id,
            max_users=model.max_users,
            max_documents=model.max_documents,
        )

    @staticmethod
    def org_to_model(entity: OrganizationEntity) -> OrganizationModel:
        return OrganizationModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            slug=str(entity.slug),
            plan=entity.plan.value,
            status=entity.status.value,
            owner_id=entity.owner_id,
            max_users=entity.max_users,
            max_documents=entity.max_documents,
        )

    # -----------------------------------------------------------------------
    # Document Mapper
    # -----------------------------------------------------------------------
    @staticmethod
    def doc_to_entity(model: DocumentModel) -> DocumentEntity:
        return DocumentEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            uploader_id=model.uploader_id,
            title=model.title,
            filename=model.filename,
            document_type=DocumentType(model.document_type),
            mime_type=model.mime_type,
            file_size=FileSize(model.file_size_bytes),
            storage_path=StoragePath(model.storage_path),
            status=DocumentStatus(model.status),
            page_count=model.page_count,
            chunk_count=model.chunk_count,
            elasticsearch_index=model.elasticsearch_index,
            error_message=model.error_message,
        )

    @staticmethod
    def doc_to_model(entity: DocumentEntity) -> DocumentModel:
        return DocumentModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            organization_id=entity.organization_id or uuid.uuid4(),  # non-nullable in model
            uploader_id=entity.uploader_id,
            title=entity.title,
            filename=entity.filename,
            document_type=entity.document_type.value,
            mime_type=entity.mime_type,
            file_size_bytes=entity.file_size.bytes,
            storage_path=str(entity.storage_path),
            status=entity.status.value,
            page_count=entity.page_count,
            chunk_count=entity.chunk_count,
            elasticsearch_index=entity.elasticsearch_index,
            error_message=entity.error_message,
        )

    # -----------------------------------------------------------------------
    # Conversation & Message Mappers
    # -----------------------------------------------------------------------
    @staticmethod
    def message_to_entity(model: MessageModel) -> MessageEntity:
        return MessageEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            conversation_id=model.conversation_id,
            role=MessageRole(model.role),
            content=model.content,
            token_count=model.token_count,
            model=model.model,
        )

    @staticmethod
    def message_to_model(entity: MessageEntity) -> MessageModel:
        return MessageModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            conversation_id=entity.conversation_id,
            role=entity.role.value,
            content=entity.content,
            token_count=entity.token_count,
            model=entity.model,
        )

    @staticmethod
    def conv_to_entity(model: ConversationModel) -> ConversationEntity:
        return ConversationEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            user_id=model.user_id,
            title=model.title,
            status=ConversationStatus(model.status),
            messages=[DataMapper.message_to_entity(m) for m in model.messages] if model.messages else [],
        )

    @staticmethod
    def conv_to_model(entity: ConversationEntity) -> ConversationModel:
        return ConversationModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            organization_id=entity.organization_id or uuid.uuid4(),  # non-nullable in model
            user_id=entity.user_id or uuid.uuid4(),  # non-nullable in model
            title=entity.title,
            status=entity.status.value,
        )

    # -----------------------------------------------------------------------
    # API Key Mapper
    # -----------------------------------------------------------------------
    @staticmethod
    def api_key_to_entity(model: ApiKeyModel) -> ApiKeyEntity:
        return ApiKeyEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization_id=model.organization_id,
            user_id=model.user_id,
            name=model.name,
            key_hash=model.key_hash,
            prefix=model.prefix,
            is_active=model.is_active,
            expires_at=model.expires_at,
            last_used_at=model.last_used_at,
            scopes=model.scopes,
        )

    @staticmethod
    def api_key_to_model(entity: ApiKeyEntity) -> ApiKeyModel:
        return ApiKeyModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            organization_id=entity.organization_id or uuid.uuid4(),  # non-nullable
            user_id=entity.user_id or uuid.uuid4(),  # non-nullable
            name=entity.name,
            key_hash=entity.key_hash,
            prefix=entity.prefix,
            is_active=entity.is_active,
            expires_at=entity.expires_at,
            last_used_at=entity.last_used_at,
            scopes=entity.scopes,
        )

    # -----------------------------------------------------------------------
    # Audit Log Mapper
    # -----------------------------------------------------------------------
    @staticmethod
    def audit_to_entity(model: AuditLogModel) -> AuditLogEntity:
        return AuditLogEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            action=AuditAction(model.action),
            actor_id=model.actor_id,
            actor_type=model.actor_type,
            organization_id=model.organization_id,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            metadata=model.metadata,
            success=model.success,
            error_message=model.error_message,
        )

    @staticmethod
    def audit_to_model(entity: AuditLogEntity) -> AuditLogModel:
        return AuditLogModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            action=entity.action.value,
            actor_id=entity.actor_id,
            actor_type=entity.actor_type,
            organization_id=entity.organization_id,
            resource_type=entity.resource_type,
            resource_id=entity.resource_id,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            metadata=entity.metadata,
            success=entity.success,
            error_message=entity.error_message,
        )

    # -----------------------------------------------------------------------
    # Role & Permission Mappers
    # -----------------------------------------------------------------------
    @staticmethod
    def role_to_entity(model: RoleModel) -> RoleEntity:
        return RoleEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            description=model.description,
            organization_id=model.organization_id,
            permission_ids={perm.id for perm in model.permissions} if model.permissions else set(),
            is_system=model.is_system,
        )

    @staticmethod
    def role_to_model(entity: RoleEntity) -> RoleModel:
        return RoleModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            description=entity.description,
            organization_id=entity.organization_id,
            is_system=entity.is_system,
        )

    @staticmethod
    def permission_to_entity(model: PermissionModel) -> PermissionEntity:
        return PermissionEntity(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            description=model.description,
            resource=model.resource,
            action=model.action,
        )

    @staticmethod
    def permission_to_model(entity: PermissionEntity) -> PermissionModel:
        return PermissionModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            description=entity.description,
            resource=entity.resource,
            action=entity.action,
        )

