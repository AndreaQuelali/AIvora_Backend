"""Global FastAPI exception handlers.

Registers handlers for all ``AppException`` subclasses and common FastAPI
validation errors, ensuring every error response follows the standard envelope:

    {
        "success": false,
        "error": {
            "code": "NOT_FOUND",
            "detail": "Document not found: abc123"
        },
        "request_id": "01JXYZ..."
    }
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.exceptions.base import AppException

logger = get_logger(__name__)


def _error_response(
    request: Request,
    status_code: int,
    error_code: str,
    detail: str,
) -> ORJSONResponse:
    """Build a standardized JSON error response."""
    request_id = request.headers.get("X-Request-ID", "")
    return ORJSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": error_code, "detail": detail},
            "request_id": request_id,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
        logger.warning(
            "Application exception",
            error_code=exc.error_code,
            detail=exc.detail,
            path=request.url.path,
        )
        return _error_response(request, exc.status_code, exc.error_code, exc.detail)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> ORJSONResponse:
        logger.warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=str(exc.detail),
            path=request.url.path,
        )
        return _error_response(
            request,
            exc.status_code,
            "HTTP_ERROR",
            str(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> ORJSONResponse:
        errors = exc.errors()
        logger.warning(
            "Request validation error",
            errors=errors,
            path=request.url.path,
        )
        detail = "; ".join(
            f"{' -> '.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors
        )
        return _error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            detail,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.exception(
            "Unhandled exception",
            path=request.url.path,
            exc_info=exc,
        )
        return _error_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
        )
