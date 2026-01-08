"""add user_id to transactions

Revision ID: 85e30775dec54e78a89b491d59e7c42b
Revises: 
Create Date: 2026-01-08 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85e30775dec54e78a89b491d59e7c42b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add column as nullable first to allow adding to existing rows
    op.add_column('transactions', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # 2. Populate existing rows (copy reported_by_id to user_id as a default for existing data)
    op.execute("UPDATE transactions SET user_id = reported_by_id")
    
    # 3. Alter column to be not null
    op.alter_column('transactions', 'user_id', nullable=False, existing_type=sa.Integer())

    # 4. Create foreign key
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'user_id')
