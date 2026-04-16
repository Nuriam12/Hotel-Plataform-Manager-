"""add price to inventory_products

Revision ID: a1b2c3d4e5f6
Revises: ccdb525d75cc
Create Date: 2026-04-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ccdb525d75cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'inventory_products',
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('inventory_products', 'price')
