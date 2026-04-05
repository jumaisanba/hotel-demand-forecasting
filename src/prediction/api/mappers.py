from prediction.api.schemas import ForecastSeriesDay, ForecastResponse
from prediction.application.dto.forecast import ForecastContextDto, ForecastDayDto


def map_forecast_day_dto_to_response(dto: ForecastDayDto) -> ForecastSeriesDay:
    """Преобразует ForecastDayDto в API-схему."""
    return ForecastSeriesDay(
        day=dto.day,
        bookings=dto.bookings,
        cancellations=dto.cancellations,
    )


def map_forecast_context_to_response(dto: ForecastContextDto) -> ForecastResponse:
    """Преобразует ForecastContextDto в API-ответ."""
    return ForecastResponse(
        hotel_id=dto.hotel_id,
        history_summary=[
            map_forecast_day_dto_to_response(item)
            for item in dto.history_summary
        ],
        forecast=[
            map_forecast_day_dto_to_response(item)
            for item in dto.forecast
        ],
    )