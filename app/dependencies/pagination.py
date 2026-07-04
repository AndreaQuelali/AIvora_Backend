"""Pagination query parameter dependency."""

from __future__ import annotations

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard pagination parameters injected via FastAPI Depends."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginationParams:
    """FastAPI dependency returning PaginationParams."""
    return PaginationParams(page=page, page_size=page_size)
