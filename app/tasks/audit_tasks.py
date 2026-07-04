"""Audit logging tasks — append audit entries asynchronously."""

from __future__ import annotations

from typing import Any

from app.infrastructure.messaging.celery_app import celery_app


@celery_app.task(
    name="app.tasks.audit_tasks.log_audit_event",
    queue="default",
    ignore_result=True,
)
def log_audit_event_task(
    action: str,
    actor_id: str | None,
    organization_id: str | None,
    resource_type: str = "",
    resource_id: str = "",
    metadata: dict[str, Any] | None = None,
    success: bool = True,
    error_message: str | None = None,
) -> None:
    """Persist an audit log entry asynchronously via Celery.

    By offloading audit writes to a task queue, API response times are
    unaffected by audit log persistence latency.
    """
    # TODO: persist AuditLogEntity to DB via sync SQLAlchemy session
    pass
