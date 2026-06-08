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
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("transactions"):
        return

    column_names = {column["name"] for column in inspector.get_columns("transactions")}

    if "user_id" not in column_names:
        op.add_column("transactions", sa.Column("user_id", sa.Integer(), nullable=True))
        inspector = sa.inspect(bind)
        column_names = {column["name"] for column in inspector.get_columns("transactions")}

    if "user_id" in column_names and "reported_by_id" in column_names:
        op.execute("UPDATE transactions SET user_id = reported_by_id WHERE user_id IS NULL")

    if "user_id" in column_names:
        null_user_count = bind.execute(
            sa.text("SELECT COUNT(*) FROM transactions WHERE user_id IS NULL")
        ).scalar_one()
        if null_user_count == 0:
            op.alter_column(
                "transactions",
                "user_id",
                nullable=False,
                existing_type=sa.Integer(),
            )

    fk_exists = any(
        fk.get("referred_table") == "users"
        and fk.get("constrained_columns") == ["user_id"]
        for fk in inspector.get_foreign_keys("transactions")
    )
    if inspector.has_table("users") and "user_id" in column_names and not fk_exists:
        op.create_foreign_key(
            "fk_transactions_user_id_users",
            "transactions",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("transactions"):
        return

    column_names = {column["name"] for column in inspector.get_columns("transactions")}
    if "user_id" not in column_names:
        return

    for fk in inspector.get_foreign_keys("transactions"):
        if (
            fk.get("referred_table") == "users"
            and fk.get("constrained_columns") == ["user_id"]
            and fk.get("name")
        ):
            op.drop_constraint(fk["name"], "transactions", type_="foreignkey")

    op.drop_column("transactions", "user_id")
