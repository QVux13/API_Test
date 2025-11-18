from fastapi import APIRouter
from .v1 import auth, item, user
from core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(item.router, prefix="/items", tags=["items"])