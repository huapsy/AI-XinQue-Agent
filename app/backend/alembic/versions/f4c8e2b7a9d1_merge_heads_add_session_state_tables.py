"""merge heads and add session state tables

Revision ID: f4c8e2b7a9d1
Revises: 616b8892c1a7, d93f5eab71a2
Create Date: 2026-03-29 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4c8e2b7a9d1"
down_revision: Union[str, Sequence[str], None] = ("616b8892c1a7", "d93f5eab71a2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "session_states",
        sa.Column("session_id", sa.Text(), nullable=False),
        sa.Column("current_focus", sa.JSON(), nullable=True),
        sa.Column("semantic_summary", sa.JSON(), nullable=True),
        sa.Column("stable_state", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"]),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "session_state_history",
        sa.Column("history_id", sa.Text(), nullable=False),
        sa.Column("session_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("current_focus", sa.JSON(), nullable=True),
        sa.Column("semantic_summary", sa.JSON(), nullable=True),
        sa.Column("stable_state", sa.JSON(), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("change_summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"]),
        sa.PrimaryKeyConstraint("history_id"),
    )
    op.create_index(
        "ix_session_state_history_session_id",
        "session_state_history",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_session_state_history_session_id", table_name="session_state_history")
    op.drop_table("session_state_history")
    op.drop_table("session_states")
