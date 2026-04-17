"""add account fields to stays

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'stays',
        sa.Column('account_number', sa.Integer(), nullable=True),
    )
    op.add_column(
        'stays',
        sa.Column('additional_charge', sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column(
        'stays',
        sa.Column('additional_charge_notes', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('stays', 'additional_charge_notes')
    op.drop_column('stays', 'additional_charge')
    op.drop_column('stays', 'account_number')
