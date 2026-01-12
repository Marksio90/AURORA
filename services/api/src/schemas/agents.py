"""Schemas for multi-agent system."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CalmStepType(str, Enum):
    """Types of calming actions."""

    BREATHING = "breathing"
    BREAK = "break"
    JOURNALING = "journaling"
    MOVEMENT = "movement"
    GROUNDING = "grounding"


class CalmStep(BaseModel):
    """A single calming action suggestion."""

    type: CalmStepType
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    duration_minutes: int = Field(..., ge=1, le=30)


class DecisionOption(BaseModel):
    """A decision option with consequences."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    consequences: list[str] = Field(..., min_items=1, max_items=5)
    emotional_risk: str = Field(
        ..., description="Low/Medium/High emotional risk assessment"
    )
    confidence_level: float = Field(
        ..., ge=0.0, le=1.0, description="Agent's confidence in this option"
    )


class AgentInput(BaseModel):
    """Generic input for any agent."""

    content: str
    context: dict[str, Any] = Field(default_factory=dict)
    agent_name: str


class AgentOutput(BaseModel):
    """Generic output from any agent."""

    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    agent_name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
