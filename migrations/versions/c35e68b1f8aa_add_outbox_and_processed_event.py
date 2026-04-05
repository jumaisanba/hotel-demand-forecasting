"""Add outbox and processed event

Revision ID: c35e68b1f8aa
Revises: 42dfe07738b3
Create Date: 2026-04-05 03:47:19.372177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c35e68b1f8aa'
down_revision: Union[str, Sequence[str], None] = '42dfe07738b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('processed_event',
    sa.Column('event_id', sa.String(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('event_id'),
    schema='auth'
    )
    op.create_table('outbox_event',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('routing_key', sa.String(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(), server_default='pending', nullable=False),
    sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('last_error', sa.String(), nullable=True),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='booking'
    )
    op.create_index(op.f('ix_booking_outbox_event_event_type'), 'outbox_event', ['event_type'], unique=False, schema='booking')
    op.create_index(op.f('ix_booking_outbox_event_status'), 'outbox_event', ['status'], unique=False, schema='booking')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_booking_outbox_event_status'), table_name='outbox_event', schema='booking')
    op.drop_index(op.f('ix_booking_outbox_event_event_type'), table_name='outbox_event', schema='booking')
    op.drop_table('outbox_event', schema='booking')
    op.drop_table('processed_event', schema='auth')
