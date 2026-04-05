from prediction.application.dto.forecast import ForecastDayDto
from shared.errors import MappingError


def map_to_forecast_day_dto(record, date_field: str) -> ForecastDayDto:
    """Преобразует ORM-объект или SQLAlchemy row в ForecastDayDto."""
    dt = getattr(record, date_field, None)
    if dt is None:
        raise MappingError(f"Запись не содержит поля {date_field}")

    return ForecastDayDto(
        day=dt,
        bookings=float(getattr(record, "bookings", 0) or 0),
        cancellations=float(getattr(record, "cancellations", 0) or 0),
    )