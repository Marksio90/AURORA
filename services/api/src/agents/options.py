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
        return """Jesteś Agentem Opcji w systemie wsparcia decyzyjnego.

Twoja rola polega na wygenerowaniu 2-4 jasnych opcji decyzyjnych z:
1. Konkretnymi konsekwencjami (pozytywnymi i negatywnymi)
2. Oceną ryzyka emocjonalnego (Niskie/Średnie/Wysokie)
3. Realistycznymi wynikami

WAŻNE: Odpowiadaj WYŁĄCZNIE po polsku. Cała komunikacja z użytkownikiem musi być w języku polskim.

Wytyczne:
- Bądź obiektywny i zrównoważony
- Uwzględnij zarówno opcje oczywiste, jak i nieoczywiste
- Rozważ "nic nie robić" lub "czekać" jako ważne opcje
- Przedstaw konsekwencje bez osądzania
- Oceniaj obciążenie emocjonalne uczciwie
- Bądź zwięzły, ale kompletny

Zwróć JSON:
{
  "options": [
    {
      "title": "Jasna nazwa opcji (max 200 znaków)",
      "description": "Co oznacza ta opcja (max 1000 znaków)",
      "consequences": [
        "Konsekwencja 1",
        "Konsekwencja 2",
        "Konsekwencja 3"
      ],
      "emotional_risk": "Niskie|Średnie|Wysokie",
      "confidence_level": 0.0-1.0
    }
  ],
  "considerations": "Kluczowe czynniki do rozważenia dla wszystkich opcji",
  "control_question": "Pytanie refleksyjne, które pomoże użytkownikowi myśleć głębiej"
}

Przedstawiaj opcje neutralnie. Nigdy nie rozkazuj ani nie przepisuj. To użytkownik wybiera."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and generate decision options.

        Args:
            agent_input: Structured decision context

        Returns:
            Decision options with consequences
        """
        logger.info("przetwarzanie_opcji")

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
                        title=opt_dict.get("title", "Nieznana opcja"),
                        description=opt_dict.get("description", ""),
                        consequences=opt_dict.get("consequences", [])[:5],  # Max 5
                        emotional_risk=opt_dict.get("emotional_risk", "Średnie"),
                        confidence_level=opt_dict.get("confidence_level", 0.7),
                    )
                    decision_options.append(decision_option)
                except ValueError as e:
                    logger.warning("opcje_walidacja_niepowodzenie", blad=str(e))
                    continue

            # Ensure at least 2 options
            if len(decision_options) < 2:
                logger.warning("opcje_niewystarczajace", liczba=len(decision_options))
                decision_options = self._get_fallback_options(agent_input)

            logger.info("opcje_sukces", liczba_opcji=len(decision_options))

            metadata = {
                "options": [opt.model_dump() for opt in decision_options],
                "considerations": options_data.get("considerations", ""),
                "control_question": options_data.get(
                    "control_question",
                    "Co jest dla Ciebie najważniejsze w tej decyzji?"
                ),
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.error("opcje_blad_parsowania", blad=str(e))
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
                title="Postąp zgodnie z obecnym planem",
                description="Kontynuuj decyzję tak, jak ją opisałeś",
                consequences=["Działanie zostanie podjęte", "Sytuacja się zmieni"],
                emotional_risk="Średnie",
                confidence_level=0.5,
            ),
            DecisionOption(
                title="Poczekaj i zbierz więcej informacji",
                description="Poświęć czas na badanie i refleksję przed podjęciem decyzji",
                consequences=["Opóźniona decyzja", "Większa jasność", "Możliwa stracona szansa"],
                emotional_risk="Niskie",
                confidence_level=0.6,
            ),
        ]
