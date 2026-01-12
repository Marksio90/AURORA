"""Schemas for decision session endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.agents import CalmStep, DecisionOption


class CreateDecisionSessionRequest(BaseModel):
    """Żądanie utworzenia nowej sesji decyzyjnej (3 pytania)."""

    context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Przed jaką decyzją stoisz?",
        examples=["Czy powinienem zmienić pracę? Mam ofertę, ale tutaj jest mi wygodnie."],
    )
    options: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Jakie opcje rozważasz?",
        examples=["Zostać w obecnej pracy, Przyjąć nową ofertę, Negocjować z obecnym pracodawcą"],
    )
    stress_level: int = Field(
        ...,
        ge=1,
        le=10,
        description="Jak bardzo jesteś zestresowany/a? (1=spokojnie, 10=przytłoczony/a)",
    )
    user_id: str | None = Field(
        default=None,
        description="Opcjonalne anonimowe ID użytkownika do śledzenia historii",
    )


class NextCheckIn(BaseModel):
    """Sugerowany czas następnej wizyty."""

    suggestion: str = Field(
        ...,
        description="Sugestia w czytelnej formie (np. '30 minut', 'jutro rano')",
    )
    reasoning: str = Field(
        ..., description="Krótkie wyjaśnienie tego czasu", max_length=200
    )


class DecisionBrief(BaseModel):
    """Końcowy wynik: Podsumowanie decyzji pokazane użytkownikowi."""

    options: list[DecisionOption] = Field(..., min_items=2, max_items=4)
    calm_step: CalmStep
    control_question: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Pytanie pomagające w refleksji",
    )
    next_check_in: NextCheckIn
    disclaimer: str = Field(
        default="To jest wsparcie w podejmowaniu decyzji, a nie porada medyczna lub terapeutyczna.",
        description="Zastrzeżenie bezpieczeństwa",
    )


class DecisionSessionResponse(BaseModel):
    """Odpowiedź dla zakończonej sesji decyzyjnej."""

    id: UUID
    created_at: datetime
    user_id: str | None
    input: CreateDecisionSessionRequest
    output: DecisionBrief
    stress_level: int
    processing_time_seconds: float | None = None

    class Config:
        from_attributes = True


class ListDecisionSessionsResponse(BaseModel):
    """Stronicowana lista sesji decyzyjnych."""

    sessions: list[DecisionSessionResponse]
    total: int
    page: int = 1
    page_size: int = 20
