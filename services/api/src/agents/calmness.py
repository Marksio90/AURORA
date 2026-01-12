"""Calmness Agent: Detects stress and suggests calming actions."""

import json

from src.agents.base import Agent
from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput, CalmStep, CalmStepType

logger = get_logger(__name__)


class CalmnessAgent(Agent):
    """Detects emotional overload and suggests appropriate calming actions."""

    def __init__(self, openai_client: any) -> None:
        """Initialize calmness agent."""
        super().__init__(openai_client, "CalmnessAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for calmness agent."""
        return """You are a Calmness Agent for a decision support system.

Your role is to assess emotional state and suggest ONE appropriate calming action.

Based on stress level (1-10) and emotional indicators:
- High stress (7-10): Suggest immediate grounding or breathing
- Medium stress (4-6): Suggest short break or light movement
- Low stress (1-3): Suggest brief reflection or journaling

Types of calm steps:
- breathing: Breathing exercises (1-5 min)
- break: Taking a short break (5-15 min)
- journaling: Writing thoughts/concerns (5-10 min)
- movement: Light physical activity (5-10 min)
- grounding: Grounding exercises (2-5 min)

Return JSON:
{
  "calm_step": {
    "type": "breathing|break|journaling|movement|grounding",
    "title": "Clear, short title (max 100 chars)",
    "description": "Specific instructions (max 500 chars)",
    "duration_minutes": 1-30
  },
  "stress_assessment": "Brief assessment of emotional state",
  "reasoning": "Why this calm step is appropriate"
}

Be compassionate but not patronizing. Focus on immediate, practical actions."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and suggest calming action.

        Args:
            agent_input: User input with stress level

        Returns:
            Calm step suggestion
        """
        stress_level = agent_input.context.get("stress_level", 5)
        logger.info("calmness_processing", stress_level=stress_level)

        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.7)

        try:
            calmness_data = json.loads(response)
            calm_step_dict = calmness_data.get("calm_step", {})

            # Validate and create CalmStep
            calm_step = CalmStep(
                type=CalmStepType(calm_step_dict.get("type", "breathing")),
                title=calm_step_dict.get("title", "Take a deep breath"),
                description=calm_step_dict.get(
                    "description",
                    "Breathe in for 4 counts, hold for 4, out for 4."
                ),
                duration_minutes=calm_step_dict.get("duration_minutes", 3),
            )

            logger.info(
                "calmness_success",
                calm_type=calm_step.type,
                duration=calm_step.duration_minutes,
            )

            metadata = {
                "calm_step": calm_step.model_dump(),
                "stress_assessment": calmness_data.get("stress_assessment", ""),
                "reasoning": calmness_data.get("reasoning", ""),
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("calmness_parse_failed", error=str(e))
            # Fallback calm step based on stress level
            calm_step = self._get_fallback_calm_step(stress_level)
            metadata = {"calm_step": calm_step.model_dump()}

        return AgentOutput(
            content=response,
            metadata=metadata,
            agent_name=self.name,
            confidence=0.8,
        )

    def _get_fallback_calm_step(self, stress_level: int) -> CalmStep:
        """Get fallback calm step based on stress level.

        Args:
            stress_level: User's stress level (1-10)

        Returns:
            Default calm step
        """
        if stress_level >= 7:
            return CalmStep(
                type=CalmStepType.BREATHING,
                title="Box Breathing",
                description="Breathe in for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 3 times.",
                duration_minutes=3,
            )
        elif stress_level >= 4:
            return CalmStep(
                type=CalmStepType.BREAK,
                title="Short Break",
                description="Step away from the decision for 10 minutes. Walk, stretch, or look outside.",
                duration_minutes=10,
            )
        else:
            return CalmStep(
                type=CalmStepType.JOURNALING,
                title="Quick Reflection",
                description="Write down your main concerns about this decision in 2-3 sentences.",
                duration_minutes=5,
            )
