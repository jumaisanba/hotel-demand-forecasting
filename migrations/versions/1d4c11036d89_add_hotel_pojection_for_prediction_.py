"""Add hotel pojection for prediction service

Revision ID: 1d4c11036d89
Revises: 3fb1ad95dff0
Create Date: 2026-04-05 06:17:31.169404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d4c11036d89'
down_revision: Union[str, Sequence[str], None] = '3fb1ad95dff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('hotel_projection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city_id', sa.Integer(), nullable=False),
    sa.Column('is_city_hotel', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='forecast'
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('hotel_projection', schema='forecast')
