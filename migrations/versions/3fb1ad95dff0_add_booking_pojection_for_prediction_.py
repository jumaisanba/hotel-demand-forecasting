"""Add booking pojection for prediction service

Revision ID: 3fb1ad95dff0
Revises: c35e68b1f8aa
Create Date: 2026-04-05 06:04:01.286453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fb1ad95dff0'
down_revision: Union[str, Sequence[str], None] = 'c35e68b1f8aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('booking_projection',
    sa.Column('booking_ref', sa.String(), nullable=False),
    sa.Column('hotel_id', sa.Integer(), nullable=False),
    sa.Column('arrival_date', sa.Date(), nullable=False),
    sa.Column('lead_time', sa.Integer(), nullable=True),
    sa.Column('adr', sa.Float(), nullable=True),
    sa.Column('total_guests', sa.Integer(), nullable=True),
    sa.Column('total_nights', sa.Integer(), nullable=True),
    sa.Column('booking_changes', sa.Integer(), nullable=True),
    sa.Column('has_deposit', sa.Boolean(), nullable=True),
    sa.Column('is_cancellation', sa.Boolean(), nullable=True),
    sa.Column('market_segment', sa.String(), nullable=True),
    sa.Column('distribution_channel', sa.String(), nullable=True),
    sa.Column('reserved_room_type', sa.String(), nullable=True),
    sa.Column('day_of_week', sa.Integer(), nullable=True),
    sa.Column('source_updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('payload_hash', sa.String(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('booking_ref', 'hotel_id'),
    sa.UniqueConstraint('hotel_id', 'booking_ref', name='uq_projection_hotel_ref'),
    schema='forecast'
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('booking_projection', schema='forecast')
