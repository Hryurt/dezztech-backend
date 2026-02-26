"""add phone_number and how_did_you_hear to users

Revision ID: a1b2c3d4e5f6
Revises: 23fc1fe3f676
Create Date: 2026-02-25

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "23fc1fe3f676"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _get_column_names() -> set[str]:
    """Get current column names in users table."""
    conn = op.get_bind()
    insp = inspect(conn)
    columns = insp.get_columns("users")
    return {c["name"] for c in columns}


def upgrade() -> None:
    """Upgrade schema: add phone_number and how_did_you_hear columns."""
    columns = _get_column_names()

    # Handle phone_number: rename from 'phone' if exists, else add
    if "phone" in columns and "phone_number" not in columns:
        op.alter_column(
            "users",
            "phone",
            new_column_name="phone_number",
            existing_type=sa.String(20),
        )
    elif "phone_number" not in columns:
        op.add_column(
            "users",
            sa.Column("phone_number", sa.String(20), nullable=True),
        )

    # Handle how_did_you_hear: rename from 'heard_from' if exists, else add
    if "heard_from" in columns and "how_did_you_hear" not in columns:
        op.alter_column(
            "users",
            "heard_from",
            new_column_name="how_did_you_hear",
            existing_type=sa.String(255),
        )
    elif "how_did_you_hear" not in columns:
        op.add_column(
            "users",
            sa.Column("how_did_you_hear", sa.String(255), nullable=True),
        )


def downgrade() -> None:
    """Downgrade schema: drop phone_number and how_did_you_hear columns."""
    columns = _get_column_names()

    if "phone_number" in columns:
        op.drop_column("users", "phone_number")
    if "how_did_you_hear" in columns:
        op.drop_column("users", "how_did_you_hear")
