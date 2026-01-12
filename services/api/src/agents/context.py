"""Context Agent: Asks 0-2 clarifying questions if needed."""

import json

from src.agents.base import Agent
from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput

logger = get_logger(__name__)


class ContextAgent(Agent):
    """Determines if clarifying questions are needed (0-2 max)."""

    def __init__(self, openai_client: any) -> None:
        """Initialize context agent."""
        super().__init__(openai_client, "ContextAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for context agent."""
        return """You are a Context Agent for a decision support system.

Your role is to determine if ANY clarifying questions are needed to understand the user's decision.

IMPORTANT:
- Ask 0-2 questions ONLY if critical information is missing
- Do NOT ask questions just to be thorough
- Prefer NO questions if the decision is reasonably clear
- Focus on: missing constraints, unclear options, ambiguous goals

Return JSON:
{
  "needs_clarification": true/false,
  "questions": [
    {
      "question": "Clear, specific question",
      "reasoning": "Why this question is critical"
    }
  ],
  "missing_info": ["What's missing"]
}

Default to needs_clarification: false unless something truly critical is unclear."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and determine if clarification is needed.

        Args:
            agent_input: Structured input from intake agent

        Returns:
            Clarification questions (if any)
        """
        logger.info("context_processing")

        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.3)

        try:
            context_data = json.loads(response)
            needs_clarification = context_data.get("needs_clarification", False)
            questions = context_data.get("questions", [])

            # Enforce max 2 questions
            if len(questions) > 2:
                questions = questions[:2]
                logger.warning("context_too_many_questions", original_count=len(questions))

            logger.info(
                "context_success",
                needs_clarification=needs_clarification,
                question_count=len(questions),
            )
        except json.JSONDecodeError:
            logger.warning("context_json_parse_failed")
            context_data = {"needs_clarification": False, "questions": []}

        return AgentOutput(
            content=response,
            metadata=context_data,
            agent_name=self.name,
            confidence=0.85,
        )
