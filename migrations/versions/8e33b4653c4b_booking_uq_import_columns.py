"""booking: uq + import columns

Revision ID: 8e33b4653c4b
Revises: ddb21643973c
Create Date: 2026-03-03 20:12:00.398859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e33b4653c4b'
down_revision: Union[str, Sequence[str], None] = 'ddb21643973c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('booking', sa.Column('source_updated_at', sa.DateTime(timezone=True), nullable=True), schema='booking')
    op.add_column('booking', sa.Column('payload_hash', sa.String(), nullable=True), schema='booking')

    op.add_column("booking", sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True), schema="booking")
    # Заполняем imported_at из created_at для существующих строк
    op.execute("""
        UPDATE booking.booking
        SET imported_at = created_at
        WHERE imported_at IS NULL;
    """)
    op.alter_column('booking', 'imported_at',
                existing_type=sa.DateTime(timezone=True),
                server_default=sa.text('now()'),
                nullable=False,
                schema='booking')

    op.alter_column('booking', 'booking_ref',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='booking')
    op.create_index(op.f('ix_booking_booking_hotel_id'), 'booking', ['hotel_id'], unique=False, schema='booking')
    op.create_unique_constraint('uq_booking_hotel_ref', 'booking', ['hotel_id', 'booking_ref'], schema='booking')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_booking_hotel_ref', 'booking', schema='booking', type_='unique')
    op.drop_index(op.f('ix_booking_booking_hotel_id'), table_name='booking', schema='booking')
    op.alter_column('booking', 'booking_ref',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='booking')
    op.drop_column('booking', 'imported_at', schema='booking')
    op.drop_column('booking', 'payload_hash', schema='booking')
    op.drop_column('booking', 'source_updated_at', schema='booking')