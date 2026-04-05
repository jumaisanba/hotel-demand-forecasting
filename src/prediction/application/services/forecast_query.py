import logging
from datetime import timedelta

from prediction.application.dto.forecast import (
    ForecastContextDto,
    GetForecastContextQuery,
)
from prediction.application.mappers import map_to_forecast_day_dto
from prediction.application.ports.unit_of_work import IUnitOfWork
from shared.errors import InsufficientHistoryError, NoForecastError

logger = logging.getLogger(__name__)


class ForecastQueryService:
    """Возвращает историю бронирований и прогноз из БД prediction-сервиса."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def get_context(
        self,
        query: GetForecastContextQuery,
    ) -> ForecastContextDto:
        """Возвращает историю бронирований и прогноз для указанного отеля."""
        history_start = query.target_date - timedelta(days=query.history_window)
        forecast_end = query.target_date + timedelta(days=query.horizon - 1)

        async with self._uow:
            history_records = await self._uow.bookings_projection.get_history_summary(
                hotel_id=query.hotel_id,
                date_from=history_start,
                date_to=query.target_date,
                has_deposit=query.has_deposit,
            )

            if not history_records:
                logger.warning(
                    "История пуста: hotel_id=%s, target_date=%s",
                    query.hotel_id,
                    query.target_date,
                )
                raise InsufficientHistoryError(
                    f"Недостаточно данных для прогноза за {query.history_window} дней до {query.target_date}."
                )

            history_days = [
                map_to_forecast_day_dto(record, "arrival_date")
                for record in history_records
            ]

            total_bookings = sum(day.bookings for day in history_days)
            if total_bookings < 30:
                logger.warning(
                    "Недостаточно данных для прогноза: hotel_id=%s, bookings=%s",
                    query.hotel_id,
                    total_bookings,
                )
                raise InsufficientHistoryError(
                    f"Недостаточно данных для прогноза: всего {int(total_bookings)} бронирований."
                )

            forecast_records = await self._uow.predictions.get_forecast_range(
                hotel_id=query.hotel_id,
                date_from=query.target_date,
                date_to=forecast_end,
                has_deposit=query.has_deposit,
            )

            if not forecast_records:
                logger.warning(
                    "Прогноз пуст: hotel_id=%s, target_date=%s",
                    query.hotel_id,
                    query.target_date,
                )
                raise NoForecastError(
                    f"Прогноз отсутствует для периода {query.target_date} — {forecast_end}."
                )

            forecast_days = [
                map_to_forecast_day_dto(record, "target_date")
                for record in forecast_records
            ]

            return ForecastContextDto(
                hotel_id=query.hotel_id,
                history_summary=history_days,
                forecast=forecast_days,
            )