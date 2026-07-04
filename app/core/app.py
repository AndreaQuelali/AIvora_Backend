"""FastAPI application factory — ``create_app()``.

Follows the factory pattern to allow instantiating multiple app instances
(e.g., for testing) with different configurations.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config.settings import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.telemetry import setup_telemetry
from app.exceptions.handlers import register_exception_handlers
from app.middleware.rate_limit import register_rate_limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    configure_logging()
    setup_telemetry()

    settings = get_settings()

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        description=(
            "AIvora — SaaS AI Document Intelligence Platform. "
            "Upload, process, and query documents using natural language powered by RAG."
        ),
        docs_url="/docs" if not settings.app.is_production else None,
        redoc_url="/redoc" if not settings.app.is_production else None,
        openapi_url="/openapi.json" if not settings.app.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------------
    # Middleware (order matters — applied in reverse registration order)
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    app.add_middleware(SecurityHeadersMiddleware, is_production=settings.app.is_production)
    app.add_middleware(RequestIDMiddleware)

    # Rate limiting (registers middleware + exception handler internally)
    register_rate_limiter(app)

    # -----------------------------------------------------------------------
    # Exception handlers
    # -----------------------------------------------------------------------
    register_exception_handlers(app)

    # -----------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------
    from app.api.v1.router import api_v1_router

    app.include_router(api_v1_router, prefix="/api/v1")

    return app
