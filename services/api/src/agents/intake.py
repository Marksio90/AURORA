"""Intake Agent: Normalizes user input into structured schema."""

import json

from src.agents.base import Agent
from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput

logger = get_logger(__name__)


class IntakeAgent(Agent):
    """Normalizes and structures user input for processing."""

    def __init__(self, openai_client: any) -> None:
        """Initialize intake agent."""
        super().__init__(openai_client, "IntakeAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for intake agent."""
        return """You are an Intake Agent for a decision support system.

Your role is to normalize and structure user input into a clear, concise format.

Extract and structure:
1. Core decision question
2. Available options (list them clearly)
3. Key constraints or requirements
4. Emotional state indicators
5. Time sensitivity

Return a JSON object with these fields:
{
  "decision_question": "Clear statement of the decision",
  "options": ["Option 1", "Option 2", ...],
  "constraints": ["Constraint 1", "Constraint 2", ...],
  "emotional_indicators": ["indicator 1", "indicator 2", ...],
  "time_sensitive": true/false,
  "context_summary": "Brief summary of additional context"
}

Be objective and non-judgmental. Extract only what's explicitly stated or clearly implied."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and normalize user input.

        Args:
            agent_input: Raw user input

        Returns:
            Structured agent output
        """
        logger.info("intake_processing", input_length=len(agent_input.content))

        # Format input for LLM
        prompt = self._format_input(agent_input)

        # Call LLM
        response = await self._call_llm(prompt, temperature=0.3)

        # Parse JSON response
        try:
            structured_data = json.loads(response)
            logger.info("intake_success", decision_question=structured_data.get("decision_question", "")[:100])
        except json.JSONDecodeError:
            logger.warning("intake_json_parse_failed", response=response[:200])
            # Fallback to raw response
            structured_data = {
                "decision_question": agent_input.content[:200],
                "options": agent_input.context.get("options", "").split(","),
                "context_summary": response,
            }

        return AgentOutput(
            content=response,
            metadata=structured_data,
            agent_name=self.name,
            confidence=0.9,
        )
