"""Unit tests for orchestrator."""

import pytest

from src.orchestrator.state import DecisionState


def test_decision_state_initialization() -> None:
    """Test decision state initializes correctly."""
    state = DecisionState(
        context="Test context",
        options="Option A, Option B",
        stress_level=5,
    )

    assert state.context == "Test context"
    assert state.stress_level == 5
    assert state.current_step == "intake"
    assert len(state.completed_steps) == 0


def test_decision_state_tracks_steps() -> None:
    """Test decision state tracks completed steps."""
    state = DecisionState(
        context="Test",
        options="A, B",
        stress_level=3,
    )

    state.completed_steps.append("intake")
    state.completed_steps.append("context")
    state.current_step = "calmness"

    assert len(state.completed_steps) == 2
    assert "intake" in state.completed_steps
    assert state.current_step == "calmness"
