"""create payments table

Revision ID: c5296e1996e1
Revises: 1cc7eaab9085
Create Date: 2025-11-03 20:17:21.887066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5296e1996e1'
down_revision: Union[str, Sequence[str], None] = '1cc7eaab9085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
