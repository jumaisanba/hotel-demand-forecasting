from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from booking.application.dto.booking.parse import ParsedBookingRow


@dataclass(frozen=True, slots=True)
class ExistingBookingState:
    """Состояние существующего бронирования из БД для сравнения."""

    booking_ref: str
    payload_hash: str | None
    source_updated_at: datetime | None


class BookingRejectReason(str, Enum):
    """Причины отклонения строки бронирования."""

    MISSING_BOOKING_REF = "missing_booking_ref"
    DUPLICATE_BOOKING_REF = "duplicate_booking_ref"


@dataclass(slots=True)
class RejectedBookingRow:
    """Отклонённая строка с причиной и сообщением."""

    row: ParsedBookingRow
    reason: BookingRejectReason
    message: str | None = None


@dataclass(slots=True)
class BookingDiffResult:
    """Результат сравнения входных данных с БД (insert/update/skip/reject)."""

    to_insert: list[ParsedBookingRow] = field(default_factory=list)
    to_update: list[ParsedBookingRow] = field(default_factory=list)
    unchanged: list[ParsedBookingRow] = field(default_factory=list)
    rejected: list[RejectedBookingRow] = field(default_factory=list)
