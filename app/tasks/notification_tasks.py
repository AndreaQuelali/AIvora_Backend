"""Notification tasks — email and webhook stubs."""

from __future__ import annotations

from app.infrastructure.messaging.celery_app import celery_app


@celery_app.task(
    name="app.tasks.notification_tasks.send_email",
    queue="notifications",
    max_retries=3,
    default_retry_delay=60,
)
def send_email_task(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = "",
) -> None:
    """Send a transactional email asynchronously.

    TODO: Implement with AWS SES / SendGrid / Resend.
    """
    pass
