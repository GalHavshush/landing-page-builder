"""asset credit

Revision ID: a1b2c3d4e5f6
Revises: e34e6d9ef4d9
Create Date: 2026-10-05 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'e34e6d9ef4d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('assets', sa.Column('credit', sa.String(length=300), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('assets', 'credit')
