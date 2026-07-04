"""AIvora Backend — ASGI application entrypoint.

Uvicorn is pointed at ``app.main:app``.
"""

from __future__ import annotations

from app.core.app import create_app

app = create_app()
