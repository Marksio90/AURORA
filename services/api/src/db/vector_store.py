"""Vector similarity search using pgvector."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.models import DecisionSession

logger = get_logger(__name__)


class VectorStore:
    """Handles vector embeddings and similarity search."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize vector store with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def store_embedding(
        self, session_id: str, embedding: list[float]
    ) -> None:
        """Store embedding vector for a decision session.

        Args:
            session_id: UUID of the decision session
            embedding: Vector embedding (1536 dimensions)
        """
        stmt = (
            select(DecisionSession)
            .where(DecisionSession.id == session_id)
        )
        result = await self.session.execute(stmt)
        decision_session = result.scalar_one_or_none()

        if decision_session:
            decision_session.embedding = embedding
            await self.session.commit()
            logger.info("embedding_stored", session_id=session_id)

    async def find_similar(
        self,
        query_embedding: list[float],
        limit: int = 5,
        user_id: str | None = None,
    ) -> list[DecisionSession]:
        """Find similar decision sessions using cosine similarity.

        Args:
            query_embedding: Query vector (1536 dimensions)
            limit: Maximum number of results
            user_id: Optional filter by user ID

        Returns:
            List of similar decision sessions
        """
        # Build query with vector similarity
        stmt = select(DecisionSession).where(
            DecisionSession.embedding.isnot(None)
        )

        if user_id:
            stmt = stmt.where(DecisionSession.user_id == user_id)

        # Order by cosine distance (L2 distance normalized)
        stmt = stmt.order_by(
            DecisionSession.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        result = await self.session.execute(stmt)
        similar_sessions = result.scalars().all()

        logger.info(
            "similarity_search_completed",
            results_count=len(similar_sessions),
            user_id=user_id,
        )

        return list(similar_sessions)

    async def get_context_for_user(
        self, user_id: str, query_embedding: list[float], limit: int = 3
    ) -> dict[str, Any]:
        """Get contextual information from user's past decisions.

        Args:
            user_id: User identifier
            query_embedding: Current decision embedding
            limit: Number of past sessions to retrieve

        Returns:
            Dictionary with contextual information
        """
        similar_sessions = await self.find_similar(
            query_embedding=query_embedding,
            limit=limit,
            user_id=user_id,
        )

        if not similar_sessions:
            return {"past_decisions": [], "patterns": []}

        # Extract patterns from past decisions
        contexts = [s.context for s in similar_sessions]
        stress_levels = [s.stress_level for s in similar_sessions]

        return {
            "past_decisions": [
                {
                    "context": s.context[:200],  # Truncate for context
                    "stress_level": s.stress_level,
                    "created_at": s.created_at.isoformat(),
                }
                for s in similar_sessions
            ],
            "patterns": {
                "avg_stress_level": sum(stress_levels) / len(stress_levels),
                "decision_count": len(similar_sessions),
            },
        }
