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
        return """Jesteś Agentem Kontekstu w systemie wsparcia decyzyjnego.

Twoja rola polega na określeniu, czy potrzebne są JAKIEKOLWIEK pytania wyjaśniające, aby zrozumieć decyzję użytkownika.

WAŻNE: Odpowiadaj WYŁĄCZNIE po polsku. Cała komunikacja z użytkownikiem musi być w języku polskim.

WAŻNE:
- Zadawaj 0-2 pytania TYLKO wtedy, gdy brakuje krytycznych informacji
- NIE zadawaj pytań tylko po to, by być dokładnym
- Preferuj BRAK pytań, jeśli decyzja jest w miarę jasna
- Skup się na: brakujących ograniczeniach, niejasnych opcjach, niejednoznacznych celach

Zwróć JSON:
{
  "needs_clarification": true/false,
  "questions": [
    {
      "question": "Jasne, konkretne pytanie",
      "reasoning": "Dlaczego to pytanie jest krytyczne"
    }
  ],
  "missing_info": ["Co brakuje"]
}

Domyślnie needs_clarification: false, chyba że coś naprawdę krytycznego jest niejasne."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and determine if clarification is needed.

        Args:
            agent_input: Structured input from intake agent

        Returns:
            Clarification questions (if any)
        """
        logger.info("przetwarzanie_kontekstu")

        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.3)

        try:
            context_data = json.loads(response)
            needs_clarification = context_data.get("needs_clarification", False)
            questions = context_data.get("questions", [])

            # Enforce max 2 questions
            if len(questions) > 2:
                questions = questions[:2]
                logger.warning("kontekst_za_duzo_pytan", oryginalna_liczba=len(questions))

            logger.info(
                "kontekst_sukces",
                wymaga_wyjasnienia=needs_clarification,
                liczba_pytan=len(questions),
            )
        except json.JSONDecodeError:
            logger.warning("kontekst_blad_parsowania_json")
            context_data = {"needs_clarification": False, "questions": []}

        return AgentOutput(
            content=response,
            metadata=context_data,
            agent_name=self.name,
            confidence=0.85,
        )
