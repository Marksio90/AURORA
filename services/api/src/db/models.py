"""SQLAlchemy models for Decision Calm Engine."""

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class DecisionSession(Base):
    """A single decision session with user input and AI output."""

    __tablename__ = "decision_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # User tracking (anonymous)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Input data
    context: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)
    stress_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Output data (JSON for flexibility)
    decision_brief: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    # Metadata
    processing_time_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Vector embedding for semantic search (1536 dimensions for text-embedding-3-small)
    embedding: Mapped[Any] = mapped_column(Vector(1536), nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<DecisionSession(id={self.id}, created_at={self.created_at})>"
