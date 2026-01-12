"""Schemas for multi-agent system."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CalmStepType(str, Enum):
    """Typy kroków uspokajających."""

    BREATHING = "breathing"
    BREAK = "break"
    JOURNALING = "journaling"
    MOVEMENT = "movement"
    GROUNDING = "grounding"


class CalmStep(BaseModel):
    """Sugestia pojedynczego kroku uspokajającego."""

    type: CalmStepType
    title: str = Field(..., min_length=1, max_length=100, description="Tytuł kroku uspokajającego")
    description: str = Field(..., min_length=1, max_length=500, description="Opis kroku uspokajającego")
    duration_minutes: int = Field(..., ge=1, le=30, description="Czas trwania w minutach")


class DecisionOption(BaseModel):
    """Opcja decyzyjna z konsekwencjami."""

    title: str = Field(..., min_length=1, max_length=200, description="Tytuł opcji decyzyjnej")
    description: str = Field(..., min_length=1, max_length=1000, description="Opis opcji decyzyjnej")
    consequences: list[str] = Field(..., min_items=1, max_items=5, description="Lista konsekwencji tej opcji")
    emotional_risk: str = Field(
        ..., description="Ocena ryzyka emocjonalnego: Niskie/Średnie/Wysokie"
    )
    confidence_level: float = Field(
        ..., ge=0.0, le=1.0, description="Pewność agenta co do tej opcji"
    )


class AgentInput(BaseModel):
    """Ogólny input dla dowolnego agenta."""

    content: str = Field(..., description="Treść wejściowa dla agenta")
    context: dict[str, Any] = Field(default_factory=dict, description="Kontekst dodatkowy")
    agent_name: str = Field(..., description="Nazwa agenta")


class AgentOutput(BaseModel):
    """Ogólny output z dowolnego agenta."""

    content: str = Field(..., description="Treść wyjściowa z agenta")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadane dodatkowe")
    agent_name: str = Field(..., description="Nazwa agenta")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Pewność wyniku")
