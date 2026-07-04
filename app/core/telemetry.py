"""OpenTelemetry bootstrap.

When OTEL_ENABLED=true, configures tracing and metrics export via OTLP.
When disabled (default for local dev), this module is a no-op.

Integrations:
- FastAPI: instruments all HTTP routes automatically
- SQLAlchemy: instruments async DB calls
"""

from __future__ import annotations

from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_telemetry() -> None:
    """Configure OpenTelemetry SDK.

    All instrumentation is conditional on ``OTEL_ENABLED=true``
    to avoid performance overhead during local development.
    """
    settings = get_settings()

    if not settings.otel.enabled:
        logger.info("OpenTelemetry disabled — skipping setup")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {"service.name": settings.otel.service_name, "service.version": settings.app.version}
        )
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.otel.endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()

        logger.info(
            "OpenTelemetry configured",
            endpoint=settings.otel.endpoint,
            service=settings.otel.service_name,
        )
    except ImportError:
        logger.warning("OpenTelemetry packages not installed — skipping instrumentation")
