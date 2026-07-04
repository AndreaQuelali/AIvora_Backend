"""AI provider abstraction — interface and placeholder implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IAIProvider(ABC):
    """Abstract AI provider interface.

    Implementations for OpenAI, Anthropic, Azure OpenAI, etc. will
    implement this interface. The application layer depends only on this
    abstract class, enabling provider swapping without code changes.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a chat completion response."""
        ...

    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
    ) -> list[list[float]]:
        """Generate vector embeddings for a list of text chunks."""
        ...

    @abstractmethod
    async def count_tokens(self, text: str, *, model: str | None = None) -> int:
        """Estimate token count for the given text."""
        ...


class OpenAIProvider(IAIProvider):
    """OpenAI API provider — placeholder implementation.

    To be fully implemented when the RAG pipeline is added.
    """

    def __init__(self, api_key: str, chat_model: str, embedding_model: str) -> None:
        self._api_key = api_key
        self._chat_model = chat_model
        self._embedding_model = embedding_model

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        raise NotImplementedError("OpenAI chat completion not yet implemented.")

    async def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
    ) -> list[list[float]]:
        raise NotImplementedError("OpenAI embeddings not yet implemented.")

    async def count_tokens(self, text: str, *, model: str | None = None) -> int:
        raise NotImplementedError("Token counting not yet implemented.")


class NoOpAIProvider(IAIProvider):
    """No-op AI provider — returns empty responses for testing/local dev."""

    async def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return "[AI not configured]"

    async def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]

    async def count_tokens(self, text: str, **kwargs: Any) -> int:
        return len(text.split())
