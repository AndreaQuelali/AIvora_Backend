"""Common response schemas — standard API envelope and pagination."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class StandardResponse(BaseModel, Generic[DataT]):
    """Standard success envelope.

    All API responses are wrapped in this model for consistency:

        {
            "success": true,
            "data": { ... },
            "message": null
        }
    """

    success: bool = True
    data: DataT
    message: str | None = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated list response."""

    success: bool = True
    data: list[DataT]
    total: int
    page: int
    page_size: int
    pages: int
    message: str | None = None

    @classmethod
    def create(
        cls,
        data: list[DataT],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[DataT]":
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(data=data, total=total, page=page, page_size=page_size, pages=pages)


class MessageResponse(BaseModel):
    """Simple message-only response."""

    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    error: dict[str, str]
    request_id: str = ""
