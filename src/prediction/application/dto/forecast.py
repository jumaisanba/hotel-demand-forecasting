from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=True)
class ForecastDayDto:
    """День истории или прогноза."""

    day: date
    bookings: float
    cancellations: float


@dataclass(slots=True, frozen=True)
class GetForecastContextQuery:
    """Параметры запроса истории и прогноза."""

    hotel_id: int
    target_date: date
    has_deposit: bool
    horizon: int = 30
    history_window: int = 30


@dataclass(slots=True, frozen=True)
class ForecastContextDto:
    """История бронирований и прогноз для отеля."""

    hotel_id: int
    history_summary: list[ForecastDayDto]
    forecast: list[ForecastDayDto]