import logging

from fastapi import APIRouter, status

from prediction.api.schemas import ModelStatusResponse, ModelConfigResponse
from prediction.application.ml.model_loader import load_model_and_config
from prediction.config import prediction_config
from shared.errors import (
    register_errors,
    ServiceError,
    ExternalServiceError,
    ModelNotFoundError,
    ModelConfigError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/status/{hotel_id}",
    response_model=ModelStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Проверить статус модели",
)
def check_model_status(hotel_id: int) -> ModelStatusResponse:
    """Проверяет наличие модели и её конфигурации."""
    model_path = prediction_config.model_dir / f"hotel_{hotel_id}/model.pt"
    config_path = prediction_config.model_dir / f"hotel_{hotel_id}/model_config.json"

    return ModelStatusResponse(
        hotel_id=hotel_id,
        model_exists=model_path.exists(),
        config_exists=config_path.exists(),
    )


@router.get(
    "/config/{hotel_id}",
    response_model=ModelConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить конфигурацию модели",
)
@register_errors(
    ServiceError,
    ExternalServiceError,
    ModelNotFoundError,
    ModelConfigError,
)
def get_model_config(hotel_id: int) -> ModelConfigResponse:
    """Возвращает конфигурацию модели для указанного отеля."""
    logger.info("Запрос конфигурации модели для отеля %s", hotel_id)
    _, config = load_model_and_config(hotel_id)
    return ModelConfigResponse(
        hotel_id=hotel_id,
        config=config,
    )