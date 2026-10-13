"""Combine the version 1 API endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.issues import router as issues_router
from app.api.v1.endpoints.users import router as users_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(issues_router)