from fastapi import APIRouter
from app.api.v1.endpoints import health, lookup

api_router = APIRouter()

# Register sub-routers under /api/v1
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(lookup.router, prefix="/indicators", tags=["indicators"])
