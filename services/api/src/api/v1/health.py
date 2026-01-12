"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str = "0.1.0"
    service: str = "decision-calm-api"


class ReadyResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    database: str
    ai_service: str


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(status="healthy")


@router.get("/health/ready", response_model=ReadyResponse)
async def readiness_check() -> ReadyResponse:
    """Readiness probe for container orchestration.

    Returns:
        Readiness status with dependencies
    """
    # TODO: Add actual DB and OpenAI connectivity checks
    return ReadyResponse(
        ready=True,
        database="connected",
        ai_service="connected",
    )
