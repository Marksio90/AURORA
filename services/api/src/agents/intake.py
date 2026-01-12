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
        return """Jesteś Agentem Przyjmującym w systemie wsparcia decyzyjnego.

Twoja rola polega na normalizacji i strukturyzacji danych wejściowych użytkownika w przejrzysty, zwięzły format.

WAŻNE: Odpowiadaj WYŁĄCZNIE po polsku. Cała komunikacja z użytkownikiem musi być w języku polskim.

Wyodrębnij i ustrukturyzuj:
1. Główne pytanie decyzyjne
2. Dostępne opcje (wypisz je jasno)
3. Kluczowe ograniczenia lub wymagania
4. Wskaźniki stanu emocjonalnego
5. Wrażliwość czasowa

Zwróć obiekt JSON z następującymi polami:
{
  "decision_question": "Jasne sformułowanie decyzji",
  "options": ["Opcja 1", "Opcja 2", ...],
  "constraints": ["Ograniczenie 1", "Ograniczenie 2", ...],
  "emotional_indicators": ["wskaźnik 1", "wskaźnik 2", ...],
  "time_sensitive": true/false,
  "context_summary": "Krótkie podsumowanie dodatkowego kontekstu"
}

Bądź obiektywny i nie oceniaj. Wyodrębniaj tylko to, co jest wyraźnie stwierdzone lub wyraźnie sugerowane."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process and normalize user input.

        Args:
            agent_input: Raw user input

        Returns:
            Structured agent output
        """
        logger.info("przetwarzanie_intake", dlugosc_inputu=len(agent_input.content))

        # Format input for LLM
        prompt = self._format_input(agent_input)

        # Call LLM
        response = await self._call_llm(prompt, temperature=0.3)

        # Parse JSON response
        try:
            structured_data = json.loads(response)
            logger.info("intake_sukces", pytanie_decyzyjne=structured_data.get("decision_question", "")[:100])
        except json.JSONDecodeError:
            logger.warning("intake_blad_parsowania_json", odpowiedz=response[:200])
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
