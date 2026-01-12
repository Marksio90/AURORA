"""Unit tests for agents."""

import pytest

from src.agents import CalmnessAgent, IntakeAgent, OptionsAgent, SafetyAgent
from src.core.errors import ContentSafetyException
from src.schemas.agents import AgentInput
from src.services.openai_client import OpenAIClient


class MockOpenAIClient:
    """Mock OpenAI client for testing."""

    async def chat_completion(self, messages: list, **kwargs: any) -> any:
        """Mock chat completion."""

        class MockChoice:
            class MockMessage:
                content = '{"decision_question": "test", "options": ["A", "B"]}'

            message = MockMessage()

        class MockResponse:
            choices = [MockChoice()]

        return MockResponse()


@pytest.fixture
def mock_openai_client() -> MockOpenAIClient:
    """Create mock OpenAI client."""
    return MockOpenAIClient()


@pytest.mark.asyncio
async def test_intake_agent(mock_openai_client: MockOpenAIClient) -> None:
    """Test intake agent processing."""
    agent = IntakeAgent(mock_openai_client)

    agent_input = AgentInput(
        content="Should I change jobs?",
        context={"options": "Stay, Leave"},
        agent_name="IntakeAgent",
    )

    output = await agent.process(agent_input)

    assert output.agent_name == "IntakeAgent"
    assert output.content is not None


@pytest.mark.asyncio
async def test_safety_agent_blocks_dangerous_content(
    mock_openai_client: MockOpenAIClient,
) -> None:
    """Test safety agent blocks self-harm content."""
    agent = SafetyAgent(mock_openai_client)

    agent_input = AgentInput(
        content="I want to kill myself",
        context={},
        agent_name="SafetyAgent",
    )

    with pytest.raises(ContentSafetyException):
        await agent.process(agent_input)
