"""change transaction_date to timestamp

Revision ID: a76c34015579
Revises: abb410548442
Create Date: 2025-11-03 20:34:49.522296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a76c34015579'
down_revision: Union[str, Sequence[str], None] = 'abb410548442'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'transactions',
        'transaction_date',
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False
    )

def downgrade():
    op.alter_column(
        'transactions',
        'transaction_date',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        existing_nullable=False
    )
