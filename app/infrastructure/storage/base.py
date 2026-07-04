"""File storage abstraction — interface and local storage implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.config.settings import get_settings


class IFileStorage(ABC):
    """Abstract file storage interface.

    Implementations: LocalFileStorage (dev), S3Storage (AWS), GCSStorage (GCP).
    """

    @abstractmethod
    async def upload(
        self, file_bytes: bytes, destination_path: str, *, content_type: str = ""
    ) -> str:
        """Upload file bytes and return the storage path."""
        ...

    @abstractmethod
    async def download(self, storage_path: str) -> bytes:
        """Download file bytes from storage."""
        ...

    @abstractmethod
    async def delete(self, storage_path: str) -> None:
        """Delete a file from storage."""
        ...

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Check if a file exists in storage."""
        ...

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        """Return a URL or path for accessing the file."""
        ...


class LocalFileStorage(IFileStorage):
    """Local filesystem storage — for development only."""

    def __init__(self, base_dir: str | None = None) -> None:
        settings = get_settings()
        self._base = Path(base_dir or settings.storage.local_upload_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    async def upload(
        self, file_bytes: bytes, destination_path: str, *, content_type: str = ""
    ) -> str:
        target = self._base / destination_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file_bytes)
        return destination_path

    async def download(self, storage_path: str) -> bytes:
        return (self._base / storage_path).read_bytes()

    async def delete(self, storage_path: str) -> None:
        path = self._base / storage_path
        if path.exists():
            path.unlink()

    async def exists(self, storage_path: str) -> bool:
        return (self._base / storage_path).exists()

    def get_url(self, storage_path: str) -> str:
        return str(self._base / storage_path)
