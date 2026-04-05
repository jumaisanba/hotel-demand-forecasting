"""Fill payload_hash and source_updated_at

Revision ID: 42dfe07738b3
Revises: 8e33b4653c4b
Create Date: 2026-03-29 06:24:39.619129

"""
import hashlib
from datetime import datetime, date
from typing import Sequence, Union, Any

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '42dfe07738b3'
down_revision: Union[str, Sequence[str], None] = '8e33b4653c4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HASH_FIELDS = (
    "arrival_date",
    "lead_time",
    "adr",
    "total_guests",
    "total_nights",
    "booking_changes",
    "has_deposit",
    "is_cancellation",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
)


def _normalize_value(value: Any) -> str:
    if value is None:
        return "<NULL>"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, float):
        return f"{value:.6f}"

    return str(value).strip()


def _build_hash(row: sa.Row) -> str:
    payload = "|".join(
        _normalize_value(row._mapping[field])
        for field in HASH_FIELDS
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE booking.booking
            SET source_updated_at = created_at
            WHERE source_updated_at IS NULL
            """
        )
    )

    result = connection.execute(
        sa.text(
            """
            SELECT
                id,
                arrival_date,
                lead_time,
                adr,
                total_guests,
                total_nights,
                booking_changes,
                has_deposit,
                is_cancellation,
                market_segment,
                distribution_channel,
                reserved_room_type
            FROM booking.booking
            WHERE payload_hash IS NULL
            """
        )
    )

    rows = result.fetchall()

    updates = [
        {
            "id": row.id,
            "payload_hash": _build_hash(row),
        }
        for row in rows
    ]

    if updates:
        connection.execute(
            sa.text(
                """
                UPDATE booking.booking
                SET payload_hash = :payload_hash
                WHERE id = :id
                """
            ),
            updates,
        )


def downgrade() -> None:
    """Downgrade schema."""
    raise NotImplementedError(
        "Downgrade is not supported for payload_hash/source_updated_at backfill migration."
    )
