"""initial schema with pgvector

Revision ID: 001
Revises:
Create Date: 2024-01-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create decision_sessions table
    op.create_table(
        'decision_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('options', sa.Text(), nullable=False),
        sa.Column('stress_level', sa.Integer(), nullable=False),
        sa.Column('decision_brief', sa.JSON(), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_decision_sessions_user_id',
        'decision_sessions',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'ix_decision_sessions_created_at',
        'decision_sessions',
        ['created_at'],
        unique=False
    )

    # Create vector similarity index
    op.execute(
        'CREATE INDEX ix_decision_sessions_embedding '
        'ON decision_sessions USING ivfflat (embedding vector_cosine_ops) '
        'WITH (lists = 100)'
    )


def downgrade() -> None:
    op.drop_index('ix_decision_sessions_embedding', table_name='decision_sessions')
    op.drop_index('ix_decision_sessions_created_at', table_name='decision_sessions')
    op.drop_index('ix_decision_sessions_user_id', table_name='decision_sessions')
    op.drop_table('decision_sessions')
    op.execute('DROP EXTENSION IF EXISTS vector')
