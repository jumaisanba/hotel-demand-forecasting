import logging

from fastapi import APIRouter, Header, status

from prediction.api.mappers import map_forecast_context_to_response
from prediction.api.schemas import ForecastRequest, ForecastResponse
from prediction.application.dto.forecast import GetForecastContextQuery
from prediction.application.services.forecast_query import ForecastQueryService
from prediction.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from shared.errors import (
    AuthorizationError,
    NoForecastError,
    InsufficientHistoryError,
    DatabaseError,
    register_errors,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/fetch",
    response_model=ForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение истории и прогноза бронирований",
    response_description="Возвращает историю и прогноз по заданным параметрам.",
)
@register_errors(
    AuthorizationError,
    NoForecastError,
    InsufficientHistoryError,
    DatabaseError,
)
async def fetch_forecast(
    req: ForecastRequest,
    x_hotel_id: int = Header(..., alias="X-Hotel-Id"),
) -> ForecastResponse:
    """
    Возвращает историю бронирований и прогноз по заданным параметрам.
    """
    if x_hotel_id <= 0:
        raise AuthorizationError()

    service = ForecastQueryService(SQLAlchemyUnitOfWork())

    result = await service.get_context(
        GetForecastContextQuery(
            hotel_id=x_hotel_id,
            target_date=req.target_date,
            has_deposit=req.has_deposit,
            horizon=req.horizon,
            history_window=req.history_window,
        )
    )

    logger.info(
        "Прогноз успешно получен: hotel_id=%s, history=%s, forecast=%s",
        result.hotel_id,
        len(result.history_summary),
        len(result.forecast),
    )

    return map_forecast_context_to_response(result)