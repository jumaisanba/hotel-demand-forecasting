import logging
import requests
from fastapi import APIRouter, HTTPException
from router.config import PREDICTION_SERVICE_URL
from router.schemas import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run-prediction", response_model=PredictionResponse)
def run_prediction(req: PredictionRequest):
    """
    Прокси-запрос в prediction_service.
    """
    try:
        logger.info("Вызов run_prediction: %s", req.model_dump())
        response = requests.post(
            f"{PREDICTION_SERVICE_URL}/run-predict",
            json=req.model_dump(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Ошибка при обращении к prediction_service: %s", e)
        raise HTTPException(status_code=500, detail="Prediction service error")
