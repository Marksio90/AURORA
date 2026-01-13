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
    # Słowa kluczowe wskazujące na potencjalne samookaleczenie lub niebezpieczną treść
    DANGER_KEYWORDS = [
        # English keywords
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "self-harm",
        "hurt myself",
        "overdose",
        "jump off",
        # Polish keywords
        "samobójstwo",
        "samobójczy",
        "zabić się",
        "zabije się",
        "skończyć z życiem",
        "odebrać sobie życie",
        "samookaleczenie",
        "skrzywdzić się",
        "zrobić sobie krzywdę",
        "przedawkowanie",
        "skoczyć z",
        "powiesić się",
        "chcę umrzeć",
        "nie chcę żyć",
    ]

    # Authoritarian language patterns to detect
    # Wzorce autorytarnego języka do wykrywania
    AUTHORITARIAN_PATTERNS = [
        # English patterns
        r"\byou must\b",
        r"\byou should\b",
        r"\byou need to\b",
        r"\bdo this now\b",
        r"\bthis is what you have to do\b",
        # Polish patterns
        r"\bmusisz\b",
        r"\bpowinieneś\b",
        r"\bpowinnaś\b",
        r"\bpowinieneś to zrobić\b",
        r"\bpowinnaś to zrobić\b",
        r"\bzrób to teraz\b",
        r"\bto musisz zrobić\b",
        r"\bnie masz wyboru\b",
        r"\bjest tylko jedna opcja\b",
        r"\bjedyna słuszna\b",
    ]

    def __init__(self, openai_client: any) -> None:
        """Initialize safety agent."""
        super().__init__(openai_client, "SafetyAgent")

    def get_system_prompt(self) -> str:
        """Get system prompt for safety agent."""
        return """Jesteś Agentem Bezpieczeństwa w systemie wsparcia decyzyjnego.

Twoja rola polega na:
1. Walidacji treści pod kątem bezpieczeństwa (brak samookaleczeń, przemocy, niebezpiecznych porad medycznych)
2. Zapewnieniu nieautorytarnego tonu (przedstaw opcje, nigdy nie rozkazuj)
3. Weryfikacji, czy obecne są odpowiednie zastrzeżenia

WAŻNE: Odpowiadaj WYŁĄCZNIE po polsku. Cała komunikacja z użytkownikiem musi być w języku polskim.

Sprawdź:
- Treści o samookaleczeniu lub samobójstwie → ZABLOKUJ
- Diagnozy medyczne lub porady lecznicze → ZABLOKUJ
- Autorytarne rozkazy ("musisz", "powinieneś") → OZNACZ
- Brakujące zastrzeżenia → DODAJ

Zwróć JSON:
{
  "is_safe": true/false,
  "blocked_reason": "Dlaczego treść została zablokowana (jeśli dotyczy)",
  "tone_violations": ["Lista znalezionych fraz autorytarnych"],
  "needs_disclaimer": true/false,
  "recommended_action": "approve|block|revise"
}

Priorytet: Bezpieczeństwo użytkownika ponad wszystko. Bądź ostrożny."""

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Validate content safety.

        Args:
            agent_input: Content to validate

        Returns:
            Safety validation results

        Raises:
            ContentSafetyException: If content is unsafe
        """
        logger.info("przetwarzanie_bezpieczenstwa")

        # Check input for danger keywords
        input_text = agent_input.content.lower()
        for keyword in self.DANGER_KEYWORDS:
            if keyword in input_text:
                logger.warning("bezpieczenstwo_wykryto_zagrozenie", slowo_kluczowe=keyword)
                raise ContentSafetyException(
                    detail=(
                        "Wykryliśmy treść, która może wskazywać na kryzys. "
                        "Ta platforma nie jest przystosowana do wsparcia w sytuacjach kryzysowych. "
                        "Skontaktuj się z infolinią kryzysową: Polska 116 123 | Telefon Zaufania dla Dzieci i Młodzieży 116 111"
                    ),
                    blocked_reason=f"Wykryto potencjalną treść o samookaleczeniu: {keyword}",
                )

        # Check for authoritarian tone in output
        output_text = agent_input.context.get("output", "")
        tone_violations = []
        for pattern in self.AUTHORITARIAN_PATTERNS:
            matches = re.findall(pattern, output_text, re.IGNORECASE)
            if matches:
                tone_violations.extend(matches)

        if tone_violations:
            logger.warning("bezpieczenstwo_naruszenie_tonu", naruszenia=tone_violations)

        # Call LLM for deeper safety check
        prompt = self._format_input(agent_input)
        response = await self._call_llm(prompt, temperature=0.2)

        try:
            import json
            safety_data = json.loads(response)
            is_safe = safety_data.get("is_safe", True)
            blocked_reason = safety_data.get("blocked_reason", "")

            if not is_safe:
                logger.error("bezpieczenstwo_zablokowano", powod=blocked_reason)
                raise ContentSafetyException(
                    detail="Treść zablokowana ze względów bezpieczeństwa",
                    blocked_reason=blocked_reason,
                )

            logger.info(
                "bezpieczenstwo_zatwierdzono",
                naruszenia_tonu=len(tone_violations),
                wymaga_zastrzezenia=safety_data.get("needs_disclaimer", False),
            )

            metadata = {
                "is_safe": is_safe,
                "tone_violations": tone_violations,
                "needs_disclaimer": safety_data.get("needs_disclaimer", True),
                "safety_check_passed": True,
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("bezpieczenstwo_blad_parsowania", blad=str(e))
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
