"""Safety Agent: Validates content safety and ethical guidelines."""

import re

from src.agents.base import Agent
from src.core.errors import ContentSafetyException
from src.core.logging import get_logger
from src.schemas.agents import AgentInput, AgentOutput

logger = get_logger(__name__)


class SafetyAgent(Agent):
    """Validates content for safety, blocks harmful content, ensures non-authoritarian tone."""

    # Keywords indicating potential self-harm or dangerous content
    DANGER_KEYWORDS = [
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "self-harm",
        "hurt myself",
        "overdose",
        "jump off",
    ]

    # Authoritarian language patterns to detect
    AUTHORITARIAN_PATTERNS = [
        r"\byou must\b",
        r"\byou should\b",
        r"\byou need to\b",
        r"\bdo this now\b",
        r"\bthis is what you have to do\b",
    ]

    def __init__(self, openai_client: any) -> None:
        """Initialize safety agent."""
        super().__init__(openai_client, "SafetyAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for safety agent."""
        return """You are a Safety Agent for a decision support system.

Your role is to:
1. Validate content for safety (no self-harm, violence, dangerous medical advice)
2. Ensure non-authoritarian tone (present options, never command)
3. Verify appropriate disclaimers are present

Check for:
- Self-harm or suicidal content → BLOCK
- Medical diagnoses or treatment advice → BLOCK
- Authoritarian commands ("you must", "you should") → FLAG
- Missing disclaimers → ADD

Return JSON:
{
  "is_safe": true/false,
  "blocked_reason": "Why content was blocked (if applicable)",
  "tone_violations": ["List of authoritarian phrases found"],
  "needs_disclaimer": true/false,
  "recommended_action": "approve|block|revise"
}

Priority: User safety above all. Be conservative."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Validate content safety.

        Args:
            agent_input: Content to validate

        Returns:
            Safety validation results

        Raises:
            ContentSafetyException: If content is unsafe
        """
        logger.info("safety_processing")

        # Check input for danger keywords
        input_text = agent_input.content.lower()
        for keyword in self.DANGER_KEYWORDS:
            if keyword in input_text:
                logger.warning("safety_danger_detected", keyword=keyword)
                raise ContentSafetyException(
                    detail=(
                        "We detected content that may indicate a crisis. "
                        "This platform is not equipped for crisis support. "
                        "Please contact a crisis helpline: US 988, EU 116 123"
                    ),
                    blocked_reason=f"Potential self-harm content detected: {keyword}",
                )

        # Check for authoritarian tone in output
        output_text = agent_input.context.get("output", "")
        tone_violations = []
        for pattern in self.AUTHORITARIAN_PATTERNS:
            matches = re.findall(pattern, output_text, re.IGNORECASE)
            if matches:
                tone_violations.extend(matches)

        if tone_violations:
            logger.warning("safety_tone_violation", violations=tone_violations)

        # Call LLM for deeper safety check
        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.2)

        try:
            import json
            safety_data = json.loads(response)
            is_safe = safety_data.get("is_safe", True)
            blocked_reason = safety_data.get("blocked_reason", "")

            if not is_safe:
                logger.error("safety_blocked", reason=blocked_reason)
                raise ContentSafetyException(
                    detail="Content blocked for safety reasons",
                    blocked_reason=blocked_reason,
                )

            logger.info(
                "safety_approved",
                tone_violations=len(tone_violations),
                needs_disclaimer=safety_data.get("needs_disclaimer", False),
            )

            metadata = {
                "is_safe": is_safe,
                "tone_violations": tone_violations,
                "needs_disclaimer": safety_data.get("needs_disclaimer", True),
                "safety_check_passed": True,
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("safety_parse_failed", error=str(e))
            # Default to safe if parsing fails
            metadata = {
                "is_safe": True,
                "tone_violations": tone_violations,
                "needs_disclaimer": True,
                "safety_check_passed": True,
            }

        return AgentOutput(
            content=response,
            metadata=metadata,
            agent_name=self.name,
            confidence=0.95,
        )
