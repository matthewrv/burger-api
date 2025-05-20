"""Base migration

Revision ID: d52f226db850
Revises:
Create Date: 2025-05-20 11:45:59.903645

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

import app

# revision identifiers, used by Alembic.
revision: str = "d52f226db850"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ingredient",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("proteins", sa.Integer(), nullable=False),
        sa.Column("fat", sa.Integer(), nullable=False),
        sa.Column("carbohydrates", sa.Integer(), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("image", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("image_mobile", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("image_large", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("burger_word", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", app.db.utils.TZDateTime(), nullable=False),
        sa.Column("updated_at", app.db.utils.TZDateTime(), nullable=False),
        sa.Column(
            "refresh_token_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("logout_at", app.db.utils.TZDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_table(
        "order",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", app.db.utils.TZDateTime(), nullable=False),
        sa.Column("updated_at", app.db.utils.TZDateTime(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "number",
            sa.Integer(),
            sa.Identity(always=True, start=1000, maxvalue=9999, cycle=True),
            nullable=False,
        ),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_created_at"), "order", ["created_at"], unique=False)
    op.create_index(op.f("ix_order_updated_at"), "order", ["updated_at"], unique=False)
    op.create_table(
        "orderingredient",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("ingredient_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredient.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["order.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("orderingredient")
    op.drop_index(op.f("ix_order_updated_at"), table_name="order")
    op.drop_index(op.f("ix_order_created_at"), table_name="order")
    op.drop_table("order")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_table("ingredient")
