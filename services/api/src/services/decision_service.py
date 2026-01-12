"""Decision service: Business logic for decision sessions."""

import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.errors import NotFoundException
from src.core.logging import get_logger
from src.db.models import DecisionSession
from src.db.vector_store import VectorStore
from src.orchestrator import DecisionOrchestrator
from src.schemas.decision import (
    CreateDecisionSessionRequest,
    DecisionBrief,
    DecisionSessionResponse,
    ListDecisionSessionsResponse,
)
from src.services.openai_client import OpenAIClient

logger = get_logger(__name__)


class DecisionService:
    """Obsługuje tworzenie i pobieranie sesji decyzyjnych."""

    def __init__(
        self,
        db_session: AsyncSession,
        openai_client: OpenAIClient,
    ) -> None:
        """Inicjalizuje serwis decyzyjny.

        Args:
            db_session: Sesja bazy danych
            openai_client: Instancja klienta OpenAI
        """
        self.db = db_session
        self.openai_client = openai_client
        self.orchestrator = DecisionOrchestrator(openai_client)
        self.vector_store = VectorStore(db_session)

    async def create_decision_session(
        self, request: CreateDecisionSessionRequest
    ) -> DecisionSessionResponse:
        """Tworzy nową sesję decyzyjną.

        Args:
            request: Żądanie sesji decyzyjnej

        Returns:
            Kompletna sesja decyzyjna z wynikami
        """
        start_time = time.time()

        logger.info(
            "tworzenie_sesji_decyzyjnej",
            stress_level=request.stress_level,
            has_user_id=request.user_id is not None,
        )

        # Run through orchestrator
        decision_brief = await self.orchestrator.process_decision(
            context=request.context,
            options=request.options,
            stress_level=request.stress_level,
            user_id=request.user_id,
        )

        processing_time = time.time() - start_time

        # Create database record
        session = DecisionSession(
            user_id=request.user_id,
            context=request.context,
            options=request.options,
            stress_level=request.stress_level,
            decision_brief=decision_brief.model_dump(),
            processing_time_seconds=processing_time,
        )

        self.db.add(session)
        await self.db.flush()  # Get ID without committing

        # Generate and store embedding if enabled
        if settings.enable_vector_search:
            try:
                # Combine context and summary for embedding
                embedding_text = f"{request.context} {request.options}"
                embedding = await self.openai_client.create_embedding(embedding_text)

                await self.vector_store.store_embedding(
                    session_id=str(session.id),
                    embedding=embedding,
                )
            except Exception as e:
                logger.warning("blad_embedding", error=str(e), session_id=session.id)

        await self.db.commit()
        await self.db.refresh(session)

        logger.info(
            "sesja_decyzyjna_utworzona",
            session_id=session.id,
            processing_time=processing_time,
        )

        return DecisionSessionResponse(
            id=session.id,
            created_at=session.created_at,
            user_id=session.user_id,
            input=request,
            output=decision_brief,
            stress_level=request.stress_level,
            processing_time_seconds=processing_time,
        )

    async def get_decision_session(self, session_id: UUID) -> DecisionSessionResponse:
        """Pobiera sesję decyzyjną według ID.

        Args:
            session_id: UUID sesji

        Returns:
            Odpowiedź sesji decyzyjnej

        Raises:
            NotFoundException: Jeśli sesja nie została znaleziona
        """
        stmt = select(DecisionSession).where(DecisionSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise NotFoundException(
                detail=f"Sesja decyzyjna {session_id} nie została znaleziona",
                resource_type="DecisionSession",
            )

        # Reconstruct request and brief
        request = CreateDecisionSessionRequest(
            context=session.context,
            options=session.options,
            stress_level=session.stress_level,
            user_id=session.user_id,
        )

        decision_brief = DecisionBrief(**session.decision_brief)

        return DecisionSessionResponse(
            id=session.id,
            created_at=session.created_at,
            user_id=session.user_id,
            input=request,
            output=decision_brief,
            stress_level=session.stress_level,
            processing_time_seconds=session.processing_time_seconds,
        )

    async def list_decision_sessions(
        self,
        user_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListDecisionSessionsResponse:
        """Wyświetla listę sesji decyzyjnych z paginacją.

        Args:
            user_id: Opcjonalny filtr według ID użytkownika
            page: Numer strony (indeksowany od 1)
            page_size: Wyników na stronę

        Returns:
            Stronicowana lista sesji
        """
        # Build query
        stmt = select(DecisionSession).order_by(DecisionSession.created_at.desc())

        if user_id:
            stmt = stmt.where(DecisionSession.user_id == user_id)

        # Get total count
        count_result = await self.db.execute(
            select(DecisionSession).where(
                DecisionSession.user_id == user_id if user_id else True
            )
        )
        total = len(count_result.scalars().all())

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        # Convert to responses
        session_responses = []
        for session in sessions:
            request = CreateDecisionSessionRequest(
                context=session.context,
                options=session.options,
                stress_level=session.stress_level,
                user_id=session.user_id,
            )
            decision_brief = DecisionBrief(**session.decision_brief)

            session_responses.append(
                DecisionSessionResponse(
                    id=session.id,
                    created_at=session.created_at,
                    user_id=session.user_id,
                    input=request,
                    output=decision_brief,
                    stress_level=session.stress_level,
                    processing_time_seconds=session.processing_time_seconds,
                )
            )

        logger.info(
            "lista_sesji_decyzyjnych",
            total=total,
            page=page,
            returned=len(session_responses),
        )

        return ListDecisionSessionsResponse(
            sessions=session_responses,
            total=total,
            page=page,
            page_size=page_size,
        )
