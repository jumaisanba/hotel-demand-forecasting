import logging
from datetime import datetime

from fastapi import APIRouter, status

from prediction.api.schemas import PredictRequest, PredictResponse
from prediction.application.services.forecast import run_forecast_for_hotel
from prediction.infrastructure.db.models import Prediction
from prediction.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from shared.errors import (
    register_errors,
    ModelConfigError,
    ModelNotFoundError,
    ValidationError,
    ServiceError,
    DatabaseError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run-predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Запустить прогнозирование",
)
@register_errors(
    ModelNotFoundError,
    ModelConfigError,
    ValidationError,
    ServiceError,
    DatabaseError,
)
async def predict(req: PredictRequest) -> PredictResponse:
    """Запускает прогнозирование для указанного отеля."""
    result = await run_forecast_for_hotel(
        hotel_id=req.hotel_id,
        uow=SQLAlchemyUnitOfWork(),
        target_date=req.target_date,
        has_deposit=req.has_deposit,
    )

    predictions = [
        Prediction(
            hotel_id=result["hotel_id"],
            target_date=datetime.fromisoformat(day["date"]).date(),
            has_deposit=req.has_deposit,
            bookings=day["bookings"],
            cancellations=day["cancellations"],
        )
        for day in result["forecast"]
    ]

    async with SQLAlchemyUnitOfWork() as uow:
        try:
            await uow.predictions.add_many(predictions)
            await uow.commit()
            logger.info(
                "Прогноз сохранён: %s записей для hotel_id=%s",
                len(predictions),
                req.hotel_id,
            )
        except Exception as exc:
            logger.exception("Ошибка при сохранении прогноза в БД: %s", exc)
            raise DatabaseError("Ошибка при сохранении прогноза в базу данных") from exc

    return PredictResponse(**result)