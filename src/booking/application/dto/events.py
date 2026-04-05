from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from uuid import uuid4

from booking.application.dto.booking.parse import ParsedBookingRow


@dataclass(frozen=True, slots=True)
class HotelCreatedEvent:
    """Событие о создании отеля и назначении владельца."""

    event_id: str
    event_type: str
    occurred_at: str
    hotel_id: int
    owner_user_id: int
    role: str = "owner"

    @classmethod
    def create(cls, *, hotel_id: int,  owner_user_id: int,) -> "HotelCreatedEvent":
        return cls(
            event_id=str(uuid4()),
            event_type="hotel.created",
            occurred_at=datetime.now(UTC).isoformat(),
            hotel_id=hotel_id,
            owner_user_id=owner_user_id,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BookingUpsertedEvent:
    """Событие об изменении бронирования для синхронизации projection."""

    event_id: str
    event_type: str
    occurred_at: str
    hotel_id: int
    booking_ref: str
    arrival_date: str
    lead_time: int | None
    adr: float | None
    total_guests: int | None
    total_nights: int | None
    booking_changes: int | None
    has_deposit: bool | None
    is_cancellation: bool | None
    market_segment: str | None
    distribution_channel: str | None
    reserved_room_type: str | None
    day_of_week: int | None
    source_updated_at: str | None
    payload_hash: str | None

    @classmethod
    def create(
        cls,
        *,
        hotel_id: int,
        row: ParsedBookingRow,
    ) -> "BookingUpsertedEvent":
        """Создаёт событие booking.upserted из строки импорта."""
        return cls(
            event_id=str(uuid4()),
            event_type="booking.upserted",
            occurred_at=datetime.now(UTC).isoformat(),
            hotel_id=hotel_id,
            booking_ref=row.booking_ref,
            arrival_date=row.arrival_date.isoformat(),
            lead_time=row.lead_time,
            adr=row.adr,
            total_guests=row.total_guests,
            total_nights=row.total_nights,
            booking_changes=row.booking_changes,
            has_deposit=row.has_deposit,
            is_cancellation=row.is_cancellation,
            market_segment=row.market_segment,
            distribution_channel=row.distribution_channel,
            reserved_room_type=row.reserved_room_type,
            day_of_week=row.arrival_date.weekday(),
            source_updated_at=(
                row.source_updated_at.isoformat()
                if row.source_updated_at is not None
                else None
            ),
            payload_hash=row.payload_hash,
        )

    def to_dict(self) -> dict:
        """Преобразует событие в словарь для payload outbox."""
        return asdict(self)
