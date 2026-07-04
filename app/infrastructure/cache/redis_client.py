"""Redis async client wrapper."""

from __future__ import annotations

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config.settings import get_settings

_redis_client: Redis | None = None  # type: ignore[type-arg]


async def get_redis_client() -> Redis:  # type: ignore[type-arg]
    """Return the module-level Redis client, creating it on first call."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis.url,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


class RedisCache:
    """High-level Redis cache operations."""

    def __init__(self, client: Redis) -> None:  # type: ignore[type-arg]
        self._client = client

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)  # type: ignore[return-value]

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        if ttl_seconds:
            await self._client.setex(key, ttl_seconds, value)
        else:
            await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def increment(self, key: str) -> int:
        return int(await self._client.incr(key))  # type: ignore[return-value]

    async def expire(self, key: str, ttl_seconds: int) -> None:
        await self._client.expire(key, ttl_seconds)

    async def ping(self) -> bool:
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
