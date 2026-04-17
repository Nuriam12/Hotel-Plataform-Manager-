"""add cancel fields to client_consumptions

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-17 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'client_consumptions',
        sa.Column('is_cancelled', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.add_column(
        'client_consumptions',
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
    )
    op.add_column(
        'client_consumptions',
        sa.Column('cancelled_by', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_consumption_cancelled_by_user',
        'client_consumptions', 'users',
        ['cancelled_by'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_consumption_cancelled_by_user', 'client_consumptions', type_='foreignkey')
    op.drop_column('client_consumptions', 'cancelled_by')
    op.drop_column('client_consumptions', 'cancelled_at')
    op.drop_column('client_consumptions', 'is_cancelled')