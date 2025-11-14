"""create transactions table

Revision ID: abb410548442
Revises: 311583ec3779
Create Date: 2025-11-03 20:28:12.746490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abb410548442'
down_revision: Union[str, Sequence[str], None] = '311583ec3779'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
