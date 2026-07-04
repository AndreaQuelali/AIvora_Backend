"""Application settings — Pydantic BaseSettings with environment-based configuration.

Follows Twelve-Factor App principles: all configuration comes from the environment.
Settings are composed into logical groups and exposed via a cached singleton.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """General application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: str = Field(default="local", alias="APP_ENV")
    name: str = Field(default="AIvora Backend", alias="APP_NAME")
    version: str = Field(default="0.1.0", alias="APP_VERSION")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    allowed_hosts: list[str] = Field(default=["*"], alias="APP_ALLOWED_HOSTS")

    @property
    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.env == "production"

    @property
    def is_local(self) -> bool:
        """Return True if running in local development."""
        return self.env == "local"


class DatabaseSettings(BaseSettings):
    """PostgreSQL / SQLAlchemy settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    host: str = Field(default="localhost", alias="DATABASE_HOST")
    port: int = Field(default=5432, alias="DATABASE_PORT")
    name: str = Field(default="aivora", alias="DATABASE_NAME")
    user: str = Field(default="aivora", alias="DATABASE_USER")
    password: str = Field(default="aivora_secret", alias="DATABASE_PASSWORD")
    pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")
    echo: bool = Field(default=False, alias="DATABASE_ECHO")

    @property
    def url(self) -> str:
        """Async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def sync_url(self) -> str:
        """Sync database URL for Alembic migrations."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Redis settings for cache and Celery broker."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: str | None = Field(default=None, alias="REDIS_PASSWORD")
    max_connections: int = Field(default=20, alias="REDIS_MAX_CONNECTIONS")

    @property
    def url(self) -> str:
        """Redis connection URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ElasticsearchSettings(BaseSettings):
    """Elasticsearch settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    hosts: list[str] = Field(default=["http://localhost:9200"], alias="ELASTICSEARCH_HOSTS")
    username: str | None = Field(default=None, alias="ELASTICSEARCH_USERNAME")
    password: str | None = Field(default=None, alias="ELASTICSEARCH_PASSWORD")
    index_prefix: str = Field(default="aivora_", alias="ELASTICSEARCH_INDEX_PREFIX")


class CelerySettings(BaseSettings):
    """Celery task queue configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    broker_url: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_BROKER_URL",
    )
    result_backend: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND",
    )
    concurrency: int = Field(default=4, alias="CELERY_CONCURRENCY")


class JWTSettings(BaseSettings):
    """JWT authentication settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    secret_key: str = Field(alias="JWT_SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )


class CORSSettings(BaseSettings):
    """CORS configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    origins: list[str] = Field(
        default=["http://localhost:3000"],
        alias="CORS_ORIGINS",
    )
    allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    allow_methods: list[str] = Field(default=["*"])
    allow_headers: list[str] = Field(default=["*"])


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    default: str = Field(default="100/minute", alias="RATE_LIMIT_DEFAULT")


class StorageSettings(BaseSettings):
    """File storage configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    backend: str = Field(default="local", alias="STORAGE_BACKEND")
    local_upload_dir: str = Field(default="./uploads", alias="STORAGE_LOCAL_UPLOAD_DIR")


class AISettings(BaseSettings):
    """AI provider configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    provider: str = Field(default="openai", alias="AI_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_chat_model: str = Field(default="gpt-4o", alias="OPENAI_CHAT_MODEL")


class OTelSettings(BaseSettings):
    """OpenTelemetry observability configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    endpoint: str = Field(
        default="http://localhost:4317",
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
    )
    service_name: str = Field(default="aivora-backend", alias="OTEL_SERVICE_NAME")


class Settings(BaseSettings):
    """Root settings object — composes all setting groups.

    Use ``get_settings()`` to access the cached singleton.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    jwt: JWTSettings = Field(default_factory=lambda: JWTSettings(JWT_SECRET_KEY="CHANGEME"))
    cors: CORSSettings = Field(default_factory=CORSSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    ai: AISettings = Field(default_factory=AISettings)
    otel: OTelSettings = Field(default_factory=OTelSettings)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton.

    The cache ensures that environment variables are read only once per process
    lifetime. In tests, use ``get_settings.cache_clear()`` to reset.
    """
    return Settings()
