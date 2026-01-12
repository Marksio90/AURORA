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
        return """Jesteś Agentem Uspokajającym w systemie wsparcia decyzyjnego.

Twoja rola polega na ocenie stanu emocjonalnego i zasugerowaniu JEDNEJ odpowiedniej akcji uspokajającej.

WAŻNE: Odpowiadaj WYŁĄCZNIE po polsku. Cała komunikacja z użytkownikiem musi być w języku polskim.

Na podstawie poziomu stresu (1-10) i wskaźników emocjonalnych:
- Wysoki stres (7-10): Zasugeruj natychmiastowe uziemienie lub oddychanie
- Średni stres (4-6): Zasugeruj krótką przerwę lub lekki ruch
- Niski stres (1-3): Zasugeruj krótką refleksję lub journaling

Typy kroków uspokajających:
- breathing: Ćwiczenia oddechowe (1-5 min)
- break: Krótka przerwa (5-15 min)
- journaling: Zapisywanie myśli/obaw (5-10 min)
- movement: Lekka aktywność fizyczna (5-10 min)
- grounding: Ćwiczenia uziemiające (2-5 min)

Zwróć JSON:
{
  "calm_step": {
    "type": "breathing|break|journaling|movement|grounding",
    "title": "Jasny, krótki tytuł (max 100 znaków)",
    "description": "Konkretne instrukcje (max 500 znaków)",
    "duration_minutes": 1-30
  },
  "stress_assessment": "Krótka ocena stanu emocjonalnego",
  "reasoning": "Dlaczego ten krok uspokajający jest odpowiedni"
}

Bądź pełen współczucia, ale nie protekcjonalny. Skup się na natychmiastowych, praktycznych działaniach."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and suggest calming action.

        Args:
            agent_input: User input with stress level

        Returns:
            Calm step suggestion
        """
        stress_level = agent_input.context.get("stress_level", 5)
        logger.info("przetwarzanie_uspokojenia", poziom_stresu=stress_level)

        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.7)

        try:
            calmness_data = json.loads(response)
            calm_step_dict = calmness_data.get("calm_step", {})

            # Validate and create CalmStep
            calm_step = CalmStep(
                type=CalmStepType(calm_step_dict.get("type", "breathing")),
                title=calm_step_dict.get("title", "Weź głęboki oddech"),
                description=calm_step_dict.get(
                    "description",
                    "Wdech na 4 oddechy, wstrzymaj na 4, wydech na 4."
                ),
                duration_minutes=calm_step_dict.get("duration_minutes", 3),
            )

            logger.info(
                "uspokojenie_sukces",
                typ_uspokojenia=calm_step.type,
                czas_trwania=calm_step.duration_minutes,
            )

            metadata = {
                "calm_step": calm_step.model_dump(),
                "stress_assessment": calmness_data.get("stress_assessment", ""),
                "reasoning": calmness_data.get("reasoning", ""),
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("uspokojenie_blad_parsowania", blad=str(e))
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
                title="Oddychanie kwadratowe",
                description="Wdech na 4 oddechy, wstrzymaj na 4, wydech na 4, wstrzymaj na 4. Powtórz 3 razy.",
                duration_minutes=3,
            )
        elif stress_level >= 4:
            return CalmStep(
                type=CalmStepType.BREAK,
                title="Krótka przerwa",
                description="Odejdź od decyzji na 10 minut. Przejdź się, rozciągnij lub popatrz przez okno.",
                duration_minutes=10,
            )
        else:
            return CalmStep(
                type=CalmStepType.JOURNALING,
                title="Szybka refleksja",
                description="Zapisz swoje główne obawy dotyczące tej decyzji w 2-3 zdaniach.",
                duration_minutes=5,
            )
