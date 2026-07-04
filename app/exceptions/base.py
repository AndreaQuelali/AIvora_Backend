"""Custom exception hierarchy for AIvora Backend.

All domain and application exceptions inherit from ``AppException``,
which carries an HTTP status code, error code, and detail message.
This allows the global exception handler to produce consistent error responses.
"""

from __future__ import annotations

from http import HTTPStatus


class AppException(Exception):
    """Base exception for all application-specific errors.

    Attributes:
        status_code: HTTP status code to return in the response.
        error_code: Machine-readable error identifier (e.g. "USER_NOT_FOUND").
        detail: Human-readable description of the error.
    """

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or "An unexpected error occurred."
        super().__init__(self.detail)


# ---------------------------------------------------------------------------
# 4xx Client Errors
# ---------------------------------------------------------------------------


class NotFoundError(AppException):
    """Resource was not found (404)."""

    status_code = HTTPStatus.NOT_FOUND.value
    error_code = "NOT_FOUND"

    def __init__(self, resource: str = "Resource", resource_id: str | None = None) -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail += f": {resource_id}"
        super().__init__(detail)


class UnauthorizedError(AppException):
    """Authentication required or token invalid (401)."""

    status_code = HTTPStatus.UNAUTHORIZED.value
    error_code = "UNAUTHORIZED"

    def __init__(self, detail: str = "Authentication required.") -> None:
        super().__init__(detail)


class ForbiddenError(AppException):
    """Authenticated user lacks required permission (403)."""

    status_code = HTTPStatus.FORBIDDEN.value
    error_code = "FORBIDDEN"

    def __init__(self, detail: str = "You do not have permission to perform this action.") -> None:
        super().__init__(detail)


class ConflictError(AppException):
    """Resource already exists or state conflict (409)."""

    status_code = HTTPStatus.CONFLICT.value
    error_code = "CONFLICT"

    def __init__(self, detail: str = "Resource already exists.") -> None:
        super().__init__(detail)


class UnprocessableEntityError(AppException):
    """Business rule violation — valid syntax but invalid semantics (422)."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    error_code = "UNPROCESSABLE_ENTITY"


class RateLimitError(AppException):
    """Too many requests (429)."""

    status_code = HTTPStatus.TOO_MANY_REQUESTS.value
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(detail)


class BadRequestError(AppException):
    """Malformed request (400)."""

    status_code = HTTPStatus.BAD_REQUEST.value
    error_code = "BAD_REQUEST"


# ---------------------------------------------------------------------------
# Domain-Specific Errors
# ---------------------------------------------------------------------------


class AuthenticationError(UnauthorizedError):
    """Invalid credentials or expired token."""

    error_code = "AUTHENTICATION_FAILED"


class TokenExpiredError(UnauthorizedError):
    """JWT token has expired."""

    error_code = "TOKEN_EXPIRED"

    def __init__(self) -> None:
        super().__init__("Token has expired.")


class TokenInvalidError(UnauthorizedError):
    """JWT token is malformed or has invalid signature."""

    error_code = "TOKEN_INVALID"

    def __init__(self) -> None:
        super().__init__("Invalid token.")


class UserAlreadyExistsError(ConflictError):
    """User with given email already exists."""

    error_code = "USER_ALREADY_EXISTS"

    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists.")


class OrganizationNotFoundError(NotFoundError):
    """Organization not found."""

    error_code = "ORGANIZATION_NOT_FOUND"

    def __init__(self, org_id: str | None = None) -> None:
        super().__init__("Organization", org_id)


class DocumentNotFoundError(NotFoundError):
    """Document not found."""

    error_code = "DOCUMENT_NOT_FOUND"

    def __init__(self, doc_id: str | None = None) -> None:
        super().__init__("Document", doc_id)


class InsufficientPermissionsError(ForbiddenError):
    """User does not have the required role/permission."""

    error_code = "INSUFFICIENT_PERMISSIONS"

    def __init__(self, required_roles: list[str] | None = None) -> None:
        if required_roles:
            detail = f"Required roles: {', '.join(required_roles)}"
        else:
            detail = "Insufficient permissions."
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Infrastructure Errors
# ---------------------------------------------------------------------------


class DatabaseError(AppException):
    """Unrecoverable database error."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "DATABASE_ERROR"


class CacheError(AppException):
    """Redis cache error (non-fatal in most cases)."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "CACHE_ERROR"


class StorageError(AppException):
    """File storage error."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "STORAGE_ERROR"


class AIProviderError(AppException):
    """AI provider API error."""

    status_code = HTTPStatus.BAD_GATEWAY.value
    error_code = "AI_PROVIDER_ERROR"
