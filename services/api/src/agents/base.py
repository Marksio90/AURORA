"""Base agent interface for multi-agent system."""

from abc import ABC, abstractmethod
from typing import Any

from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput
from src.services.openai_client import OpenAIClient

logger = get_logger(__name__)


class Agent(ABC):
    """Base class for all decision processing agents."""

    def __init__(self, openai_client: OpenAIClient, name: str) -> None:
        """Initialize agent with OpenAI client.

        Args:
            openai_client: Configured OpenAI client
            name: Agent name for logging
        """
        self.openai_client = openai_client
        self.name = name
        logger.info("agent_initialized", agent_name=name)

    @abstractmethod
    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process input and return output.

        Args:
            agent_input: Standardized agent input

        Returns:
            Standardized agent output
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent.

        Returns:
            System prompt text
        """
        pass

    async def _call_llm(
        self,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Call LLM with agent's system prompt.

        Args:
            user_message: User message content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response content
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        response = await self.openai_client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def _format_input(self, agent_input: AgentInput) -> str:
        """Format agent input into LLM prompt.

        Args:
            agent_input: Standardized agent input

        Returns:
            Formatted prompt string
        """
        context_str = "\n".join(
            f"{key}: {value}" for key, value in agent_input.context.items()
        )
        return f"{agent_input.content}\n\nContext:\n{context_str}"
