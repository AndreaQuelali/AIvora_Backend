"""Celery worker bootstrap — used as the entry point for the worker process.

Run with: celery -A app.workers.celery_worker:celery_app worker --loglevel=info
"""

from __future__ import annotations

from app.infrastructure.messaging.celery_app import celery_app  # noqa: F401 — re-exported

# Configure Django-style autodiscovery (tasks are imported via celery_app.include)
