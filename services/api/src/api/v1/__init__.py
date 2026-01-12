"""API v1 routes."""

from fastapi import APIRouter

from src.api.v1 import decision, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(decision.router, prefix="/decision", tags=["decisions"])

__all__ = ["api_router"]
