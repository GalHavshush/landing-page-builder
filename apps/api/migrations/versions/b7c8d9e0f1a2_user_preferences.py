"""user preferences

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-10-06 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("ui_language", sa.String(length=8), nullable=False, server_default="en"))
    op.add_column("users", sa.Column("ui_theme", sa.String(length=8), nullable=False, server_default="system"))


def downgrade() -> None:
    op.drop_column("users", "ui_theme")
    op.drop_column("users", "ui_language")
