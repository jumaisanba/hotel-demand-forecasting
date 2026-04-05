import logging

from fastapi import APIRouter, status

from prediction.api.schemas import TrainRequest, TrainResponse, InitHotelResponse
from prediction.application.services.trainer import (
    train_model_for_hotel,
    setup_hotel_model_from_base,
)
from prediction.config import prediction_config
from prediction.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from shared.errors import register_errors, ServiceError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/train",
    response_model=TrainResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Обучить модель отеля",
)
@register_errors(ServiceError)
async def train(req: TrainRequest) -> TrainResponse:
    """Обучает или дообучает модель для отеля."""
    if req.init:
        setup_hotel_model_from_base(req.hotel_id)

    await train_model_for_hotel(
        hotel_id=req.hotel_id,
        uow=SQLAlchemyUnitOfWork(),
        epochs=req.epochs,
        batch_size=req.batch_size,
    )

    return TrainResponse(
        hotel_id=req.hotel_id,
        message="Model fine-tuned and saved",
    )


@router.post(
    "/init-hotel/{hotel_id}",
    response_model=InitHotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Инициализировать модель отеля",
)
@register_errors(ServiceError)
def init_hotel(hotel_id: int) -> InitHotelResponse:
    """Инициализирует директорию модели для нового отеля."""
    logger.info("Инициализация модели для отеля %s", hotel_id)
    setup_hotel_model_from_base(hotel_id)

    return InitHotelResponse(
        hotel_id=hotel_id,
        path=str(prediction_config.model_dir / f"hotel_{hotel_id}"),
    )