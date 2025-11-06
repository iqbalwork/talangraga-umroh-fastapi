"""create payments table

Revision ID: 7f91f005cc0d
Revises: c5296e1996e1
Create Date: 2025-11-03 20:20:29.257477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f91f005cc0d'
down_revision: Union[str, Sequence[str], None] = 'c5296e1996e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
