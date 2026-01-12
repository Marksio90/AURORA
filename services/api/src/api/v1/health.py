"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    """Odpowiedź sprawdzenia stanu zdrowia."""

    status: str = Field(..., description="Status serwisu")
    version: str = Field(default="0.1.0", description="Wersja API")
    service: str = Field(default="decision-calm-api", description="Nazwa serwisu")


class ReadyResponse(BaseModel):
    """Odpowiedź sprawdzenia gotowości."""

    ready: bool = Field(..., description="Czy serwis jest gotowy")
    database: str = Field(..., description="Status bazy danych")
    ai_service: str = Field(..., description="Status usługi AI")


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Podstawowy endpoint sprawdzenia stanu zdrowia.

    Returns:
        Status zdrowia serwisu
    """
    return HealthResponse(status="zdrowy")


@router.get("/health/ready", response_model=ReadyResponse)
async def readiness_check() -> ReadyResponse:
    """Sonda gotowości dla orkiestracji kontenerów.

    Returns:
        Status gotowości z zależnościami
    """
    # TODO: Dodać rzeczywiste sprawdzanie połączenia z DB i OpenAI
    return ReadyResponse(
        ready=True,
        database="połączona",
        ai_service="połączona",
    )
