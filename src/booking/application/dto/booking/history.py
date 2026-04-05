from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=True)
class GetBookingDailyStatsQuery:
    """Параметры запроса агрегированной статистики бронирований."""

    hotel_id: int
    date_from: date
    date_to: date
    has_deposit: bool | None = None


@dataclass(slots=True, frozen=True)
class BookingDailyStats:
    """Агрегированная статистика бронирований за день."""

    arrival_date: date
    bookings: int
    cancellations: int
