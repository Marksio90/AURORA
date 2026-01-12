"""State management for decision orchestration."""

from typing import Any

from pydantic import BaseModel, Field


class DecisionState(BaseModel):
    """Shared state passed between agents in orchestration graph."""

    # Input data
    context: str
    options: str
    stress_level: int
    user_id: str | None = None

    # Agent outputs
    intake_output: dict[str, Any] = Field(default_factory=dict)
    context_output: dict[str, Any] = Field(default_factory=dict)
    calmness_output: dict[str, Any] = Field(default_factory=dict)
    options_output: dict[str, Any] = Field(default_factory=dict)
    safety_output: dict[str, Any] = Field(default_factory=dict)

    # Final result
    decision_brief: dict[str, Any] | None = None

    # Metadata
    processing_errors: list[str] = Field(default_factory=list)
    current_step: str = "intake"
    completed_steps: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
