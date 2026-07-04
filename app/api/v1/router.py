"""Master API v1 router — includes all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.admin.router import router as admin_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.chat.router import router as chat_router
from app.api.v1.documents.router import router as documents_router
from app.api.v1.health.router import router as health_router
from app.api.v1.organizations.router import router as organizations_router
from app.api.v1.search.router import router as search_router
from app.api.v1.users.router import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(admin_router)
