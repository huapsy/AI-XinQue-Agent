"""add clinical_profile to user_profiles

Revision ID: 7b8d8ad9c2c1
Revises: 3fd615485238
Create Date: 2026-03-28 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b8d8ad9c2c1'
down_revision: Union[str, Sequence[str], None] = '3fd615485238'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_profiles', sa.Column('clinical_profile', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_profiles', 'clinical_profile')
