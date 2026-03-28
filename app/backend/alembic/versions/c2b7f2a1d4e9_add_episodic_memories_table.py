"""add episodic_memories table

Revision ID: c2b7f2a1d4e9
Revises: 7b8d8ad9c2c1
Create Date: 2026-03-28 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2b7f2a1d4e9'
down_revision: Union[str, Sequence[str], None] = '7b8d8ad9c2c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'episodic_memories',
        sa.Column('memory_id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('session_id', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=True),
        sa.Column('emotions', sa.JSON(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('memory_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('episodic_memories')
