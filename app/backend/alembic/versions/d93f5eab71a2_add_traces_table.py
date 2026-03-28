"""add traces table

Revision ID: d93f5eab71a2
Revises: c2b7f2a1d4e9
Create Date: 2026-03-28 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd93f5eab71a2'
down_revision: Union[str, Sequence[str], None] = 'c2b7f2a1d4e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'traces',
        sa.Column('trace_id', sa.Text(), nullable=False),
        sa.Column('session_id', sa.Text(), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('input_safety', sa.JSON(), nullable=True),
        sa.Column('llm_call', sa.JSON(), nullable=True),
        sa.Column('output_safety', sa.JSON(), nullable=True),
        sa.Column('total_latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id']),
        sa.PrimaryKeyConstraint('trace_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('traces')
