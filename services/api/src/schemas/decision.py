"""Schemas for decision session endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.agents import CalmStep, DecisionOption


class CreateDecisionSessionRequest(BaseModel):
    """Request to create a new decision session (3 questions)."""

    context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="What decision are you facing?",
        examples=["Should I change jobs? I have an offer but I'm comfortable here."],
    )
    options: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="What options are you considering?",
        examples=["Stay at current job, Take new offer, Negotiate with current employer"],
    )
    stress_level: int = Field(
        ...,
        ge=1,
        le=10,
        description="How stressed do you feel? (1=calm, 10=overwhelmed)",
    )
    user_id: str | None = Field(
        default=None,
        description="Optional anonymous user ID for history tracking",
    )


class NextCheckIn(BaseModel):
    """Suggested next check-in time."""

    suggestion: str = Field(
        ...,
        description="Human-readable suggestion (e.g., '30 minutes', 'tomorrow morning')",
    )
    reasoning: str = Field(
        ..., description="Brief explanation for this timing", max_length=200
    )


class DecisionBrief(BaseModel):
    """The final output: Decision Brief shown to user."""

    options: list[DecisionOption] = Field(..., min_items=2, max_items=4)
    calm_step: CalmStep
    control_question: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="A question to help user reflect",
    )
    next_check_in: NextCheckIn
    disclaimer: str = Field(
        default="This is decision support, not medical or therapeutic advice.",
        description="Safety disclaimer",
    )


class DecisionSessionResponse(BaseModel):
    """Response for a completed decision session."""

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
    """Paginated list of decision sessions."""

    sessions: list[DecisionSessionResponse]
    total: int
    page: int = 1
    page_size: int = 20
