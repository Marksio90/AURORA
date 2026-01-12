"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "decision-calm-api"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    """Test readiness check endpoint."""
    response = await client.get("/v1/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data


@pytest.mark.asyncio
async def test_create_decision_session_validation(client: AsyncClient) -> None:
    """Test decision session creation with invalid data."""
    response = await client.post(
        "/v1/decision/sessions",
        json={
            "context": "Too short",  # Should fail min_length
            "options": "A",
            "stress_level": 5,
        },
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_decision_sessions_empty(client: AsyncClient) -> None:
    """Test listing sessions when database is empty."""
    response = await client.get("/v1/decision/sessions")

    assert response.status_code == 200
    data = response.json()
    assert data["sessions"] == []
    assert data["total"] == 0
