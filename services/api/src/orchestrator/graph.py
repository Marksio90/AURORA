"""Decision orchestrator using multi-agent graph."""

from typing import Any

from src.agents import (
    CalmnessAgent,
    ContextAgent,
    IntakeAgent,
    OptionsAgent,
    SafetyAgent,
)
from src.core.logging import get_logger
from src.orchestrator.state import DecisionState
from src.schemas.agents import AgentInput, CalmStep, DecisionOption
from src.schemas.decision import DecisionBrief, NextCheckIn
from src.services.openai_client import OpenAIClient

logger = get_logger(__name__)


class DecisionOrchestrator:
    """Orchestrates the multi-agent decision processing pipeline."""

    def __init__(self, openai_client: OpenAIClient) -> None:
        """Initialize orchestrator with agents.

        Args:
            openai_client: Configured OpenAI client
        """
        self.openai_client = openai_client

        # Initialize agents
        self.intake_agent = IntakeAgent(openai_client)
        self.context_agent = ContextAgent(openai_client)
        self.calmness_agent = CalmnessAgent(openai_client)
        self.options_agent = OptionsAgent(openai_client)
        self.safety_agent = SafetyAgent(openai_client)

        logger.info("orchestrator_zainicjalizowany")

    async def process_decision(
        self,
        context: str,
        options: str,
        stress_level: int,
        user_id: str | None = None,
    ) -> DecisionBrief:
        """Process a decision through the multi-agent pipeline.

        Args:
            context: User's decision context
            options: User's available options
            stress_level: User's stress level (1-10)
            user_id: Optional user identifier

        Returns:
            Complete decision brief

        Raises:
            ContentSafetyException: If content fails safety check
        """
        # Initialize state
        state = DecisionState(
            context=context,
            options=options,
            stress_level=stress_level,
            user_id=user_id,
        )

        logger.info("orchestration_started", stress_level=stress_level)

        # Step 1: Intake Agent - Normalize input
        state = await self._run_intake(state)

        # Step 2: Context Agent - Check if clarification needed (MVP: skip for now)
        state = await self._run_context(state)

        # Step 3: Calmness Agent - Generate calm step
        state = await self._run_calmness(state)

        # Step 4: Options Agent - Generate decision options
        state = await self._run_options(state)

        # Step 5: Safety Agent - Validate everything
        state = await self._run_safety(state)

        # Step 6: Assemble final decision brief
        decision_brief = self._assemble_decision_brief(state)

        logger.info(
            "orchestration_completed",
            option_count=len(decision_brief.options),
            calm_type=decision_brief.calm_step.type,
        )

        return decision_brief

    async def _run_intake(self, state: DecisionState) -> DecisionState:
        """Run intake agent.

        Args:
            state: Current decision state

        Returns:
            Updated state
        """
        logger.info("orchestration_step", step="intake")

        agent_input = AgentInput(
            content=state.context,
            context={"options": state.options, "stress_level": state.stress_level},
            agent_name="IntakeAgent",
        )

        output = await self.intake_agent.process(agent_input)
        state.intake_output = output.metadata
        state.completed_steps.append("intake")
        state.current_step = "context"

        return state

    async def _run_context(self, state: DecisionState) -> DecisionState:
        """Run context agent.

        Args:
            state: Current decision state

        Returns:
            Updated state
        """
        logger.info("orchestration_step", step="context")

        agent_input = AgentInput(
            content=state.context,
            context={
                "intake_output": state.intake_output,
                "stress_level": state.stress_level,
            },
            agent_name="ContextAgent",
        )

        output = await self.context_agent.process(agent_input)
        state.context_output = output.metadata
        state.completed_steps.append("context")
        state.current_step = "calmness"

        # MVP: We don't pause for clarification questions
        # In future, could return early here if needs_clarification=True

        return state

    async def _run_calmness(self, state: DecisionState) -> DecisionState:
        """Run calmness agent.

        Args:
            state: Current decision state

        Returns:
            Updated state
        """
        logger.info("orchestration_step", step="calmness")

        agent_input = AgentInput(
            content=state.context,
            context={
                "stress_level": state.stress_level,
                "intake_output": state.intake_output,
            },
            agent_name="CalmnessAgent",
        )

        output = await self.calmness_agent.process(agent_input)
        state.calmness_output = output.metadata
        state.completed_steps.append("calmness")
        state.current_step = "options"

        return state

    async def _run_options(self, state: DecisionState) -> DecisionState:
        """Run options agent.

        Args:
            state: Current decision state

        Returns:
            Updated state
        """
        logger.info("orchestration_step", step="options")

        agent_input = AgentInput(
            content=state.context,
            context={
                "options": state.options,
                "intake_output": state.intake_output,
                "stress_level": state.stress_level,
            },
            agent_name="OptionsAgent",
        )

        output = await self.options_agent.process(agent_input)
        state.options_output = output.metadata
        state.completed_steps.append("options")
        state.current_step = "safety"

        return state

    async def _run_safety(self, state: DecisionState) -> DecisionState:
        """Run safety agent.

        Args:
            state: Current decision state

        Returns:
            Updated state

        Raises:
            ContentSafetyException: If content is unsafe
        """
        logger.info("orchestration_step", step="safety")

        # Combine all content for safety check
        combined_content = f"{state.context}\n{state.options}"

        agent_input = AgentInput(
            content=combined_content,
            context={
                "output": str(state.options_output),
                "calmness_output": str(state.calmness_output),
            },
            agent_name="SafetyAgent",
        )

        output = await self.safety_agent.process(agent_input)
        state.safety_output = output.metadata
        state.completed_steps.append("safety")
        state.current_step = "complete"

        return state

    def _assemble_decision_brief(self, state: DecisionState) -> DecisionBrief:
        """Assemble final decision brief from agent outputs.

        Args:
            state: Completed decision state

        Returns:
            Decision brief for user
        """
        logger.info("assembling_decision_brief")

        # Extract options
        options_list = state.options_output.get("options", [])
        decision_options = [DecisionOption(**opt) for opt in options_list]

        # Extract calm step
        calm_step_dict = state.calmness_output.get("calm_step", {})
        calm_step = CalmStep(**calm_step_dict)

        # Extract control question
        control_question = state.options_output.get(
            "control_question",
            "Co jest dla Ciebie najważniejsze w tej decyzji?",
        )

        # Generate next check-in suggestion
        next_check_in = self._generate_next_check_in(state.stress_level)

        # Ensure disclaimer if safety flagged it
        disclaimer = (
            "⚠️ To wsparcie w podejmowaniu decyzji, nie porada medyczna ani terapeutyczna. "
            "W nagłych wypadkach: Polska 116 123 | Telefon Zaufania dla Dzieci i Młodzieży 116 111"
        )

        return DecisionBrief(
            options=decision_options,
            calm_step=calm_step,
            control_question=control_question,
            next_check_in=next_check_in,
            disclaimer=disclaimer,
        )

    def _generate_next_check_in(self, stress_level: int) -> NextCheckIn:
        """Generate next check-in suggestion based on stress level.

        Args:
            stress_level: User's stress level (1-10)

        Returns:
            Next check-in suggestion
        """
        if stress_level >= 7:
            return NextCheckIn(
                suggestion="Za 30 minut do 1 godziny",
                reasoning="Wysoki poziom stresu wymaga krótkiej przerwy przed ponownym rozważeniem",
            )
        elif stress_level >= 4:
            return NextCheckIn(
                suggestion="Za kilka godzin lub jutro rano",
                reasoning="Umiarkowany stres sugeruje, że przespanie się z tym może pomóc",
            )
        else:
            return NextCheckIn(
                suggestion="Kiedy poczujesz się gotowy/a",
                reasoning="Twój poziom stresu jest do opanowania; poświęć sobie tyle czasu, ile potrzebujesz",
            )
