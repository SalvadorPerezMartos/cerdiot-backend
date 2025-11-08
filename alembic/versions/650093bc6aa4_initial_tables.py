"""initial tables

Revision ID: 650093bc6aa4
Revises: 
Create Date: 2025-11-08 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "650093bc6aa4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(length=50), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    # --- farms ---
    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

    # --- sheds ---
    op.create_table(
        "sheds",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=False),
    )

    # --- devices ---
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("shed_id", sa.Integer(), sa.ForeignKey("sheds.id"), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("device_key", sa.String(length=100), nullable=False, unique=True, index=True),
    )

    # ⚠️ NO creamos telemetry aquí porque la tienes ya en Postgres y la excluimos en env.py


def downgrade() -> None:
    # borrar en orden inverso por claves foráneas
    op.drop_table("devices")
    op.drop_table("sheds")
    op.drop_table("farms")
    op.drop_table("users")
