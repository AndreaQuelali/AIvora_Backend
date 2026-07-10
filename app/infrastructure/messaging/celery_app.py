"""Celery application factory."""

from __future__ import annotations

from celery import Celery

from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "aivora",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        "app.tasks.document_tasks",
        "app.tasks.audit_tasks",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Re-queue task if worker crashes
    worker_prefetch_multiplier=1,  # Prevent memory spike with large payloads
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "documents"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
        "app.tasks.audit_tasks.*": {"queue": "default"},
    },
)
