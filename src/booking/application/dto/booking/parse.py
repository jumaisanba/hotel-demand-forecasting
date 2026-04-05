from dataclasses import dataclass, field, replace
from datetime import date, datetime


@dataclass(slots=True, frozen=True)
class RowParseError:
    """Ошибка парсинга строки входного файла."""

    row_number: int
    message: str


@dataclass(slots=True, frozen=True)
class ParsedBookingRow:
    """Нормализованная строка бронирования после парсинга."""

    row_number: int

    booking_ref: str
    arrival_date: date
    lead_time: int
    adr: float
    total_guests: int
    total_nights: int
    booking_changes: int
    has_deposit: bool
    is_cancellation: bool
    market_segment: str
    distribution_channel: str
    reserved_room_type: str
    source_updated_at: datetime | None = None
    payload_hash: str | None = None

    def with_payload_hash(self, payload_hash: str) -> "ParsedBookingRow":
        """Возвращает копию строки с установленным payload_hash."""
        return replace(self, payload_hash=payload_hash)


@dataclass(slots=True)
class BookingParseResult:
    """Результат парсинга входного файла."""

    parsed_rows: list[ParsedBookingRow] = field(default_factory=list)
    errors: list[RowParseError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Есть ли ошибки парсинга."""
        return bool(self.errors)

    @property
    def total_rows(self) -> int:
        """Общее количество обработанных строк."""
        return len(self.parsed_rows) + len(self.errors)
