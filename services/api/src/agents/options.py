"""Options Agent: Generates decision options with consequences."""

import json

from src.agents.base import Agent
from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput, DecisionOption

logger = get_logger(__name__)


class OptionsAgent(Agent):
    """Generates 2-4 decision options with consequences and risks."""

    def __init__(self, openai_client: any) -> None:
        """Initialize options agent."""
        super().__init__(openai_client, "OptionsAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for options agent."""
        return """You are an Options Agent for a decision support system.

Your role is to generate 2-4 clear decision options with:
1. Concrete consequences (positive and negative)
2. Emotional risk assessment (Low/Medium/High)
3. Realistic outcomes

Guidelines:
- Be objective and balanced
- Include both obvious and non-obvious options
- Consider "do nothing" or "wait" as valid options
- Present consequences without judgment
- Assess emotional toll honestly
- Be concise but complete

Return JSON:
{
  "options": [
    {
      "title": "Clear option name (max 200 chars)",
      "description": "What this option means (max 1000 chars)",
      "consequences": [
        "Consequence 1",
        "Consequence 2",
        "Consequence 3"
      ],
      "emotional_risk": "Low|Medium|High",
      "confidence_level": 0.0-1.0
    }
  ],
  "considerations": "Key factors to consider across all options",
  "control_question": "A reflective question to help user think deeper"
}

Present options neutrally. Never command or prescribe. The user chooses."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and generate decision options.

        Args:
            agent_input: Structured decision context

        Returns:
            Decision options with consequences
        """
        logger.info("options_processing")

        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.7, max_tokens=1500)

        try:
            options_data = json.loads(response)
            options_list = options_data.get("options", [])

            # Validate and create DecisionOption objects
            decision_options = []
            for opt_dict in options_list[:4]:  # Max 4 options
                try:
                    decision_option = DecisionOption(
                        title=opt_dict.get("title", "Unknown option"),
                        description=opt_dict.get("description", ""),
                        consequences=opt_dict.get("consequences", [])[:5],  # Max 5
                        emotional_risk=opt_dict.get("emotional_risk", "Medium"),
                        confidence_level=opt_dict.get("confidence_level", 0.7),
                    )
                    decision_options.append(decision_option)
                except ValueError as e:
                    logger.warning("options_validation_failed", error=str(e))
                    continue

            # Ensure at least 2 options
            if len(decision_options) < 2:
                logger.warning("options_insufficient", count=len(decision_options))
                decision_options = self._get_fallback_options(agent_input)

            logger.info("options_success", option_count=len(decision_options))

            metadata = {
                "options": [opt.model_dump() for opt in decision_options],
                "considerations": options_data.get("considerations", ""),
                "control_question": options_data.get(
                    "control_question",
                    "What matters most to you in this decision?"
                ),
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.error("options_parse_failed", error=str(e))
            decision_options = self._get_fallback_options(agent_input)
            metadata = {"options": [opt.model_dump() for opt in decision_options]}

        return AgentOutput(
            content=response,
            metadata=metadata,
            agent_name=self.name,
            confidence=0.75,
        )

    def _get_fallback_options(self, agent_input: AgentInput) -> list[DecisionOption]:
        """Generate fallback options if parsing fails.

        Args:
            agent_input: User input context

        Returns:
            List of basic decision options
        """
        return [
            DecisionOption(
                title="Move forward with current plan",
                description="Proceed with the decision as you've described it",
                consequences=["Action will be taken", "Situation will change"],
                emotional_risk="Medium",
                confidence_level=0.5,
            ),
            DecisionOption(
                title="Wait and gather more information",
                description="Take time to research and reflect before deciding",
                consequences=["Delayed decision", "More clarity", "Possible missed opportunity"],
                emotional_risk="Low",
                confidence_level=0.6,
            ),
        ]
