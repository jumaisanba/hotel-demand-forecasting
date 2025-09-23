# router/routers/data_interface_router.py

import logging
import requests
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from router.config import DATA_INTERFACE_SERVICE_URL
from router.schemas import ForecastRequest, ForecastResponse
from utils import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload-bookings")
async def upload_bookings(
    file: UploadFile = File(...),
    token_data: Dict = Depends(verify_token),
):
    """
    Проксирование загрузки бронирований в data_interface_service.
    """
    hotel_id = token_data.get("hotel_id")
    if not hotel_id:
        raise HTTPException(status_code=403, detail="hotel_id required for this action")

    files = {"file": (file.filename, file.file, file.content_type)}
    headers = {"x-hotel-id": str(hotel_id)}

    try:
        response = requests.post(
            f"{DATA_INTERFACE_SERVICE_URL}/upload/upload",
            files=files,
            headers=headers,
            timeout=10
        )
    except requests.RequestException as e:
        logger.error("Ошибка соединения с data_interface_service: %s", e)
        raise HTTPException(status_code=502, detail="Upload service connection error")

    try:
        result = response.json()
    except Exception as e:
        logger.error("Ошибка при парсинге ответа data_interface_service: %s", e)
        raise HTTPException(status_code=500, detail="Upload service response parsing error")

    if response.status_code != 200:
        detail = result.get("detail", "Unknown upload error")
        raise HTTPException(status_code=response.status_code, detail=f"Upload service error: {detail}")

    return result


@router.post("/fetch-forecast", response_model=ForecastResponse)
async def fetch_forecast(req: ForecastRequest, token_data: Dict = Depends(verify_token)):
    """
    Получение прогноза из data_interface_service.
    """
    hotel_id = token_data.get("hotel_id")
    if not hotel_id:
        raise HTTPException(status_code=403, detail="hotel_id required for this action")

    try:
        response = requests.post(
            f"{DATA_INTERFACE_SERVICE_URL}/forecast/fetch",
            json=req.model_dump(),
            headers={"x-hotel-id": str(hotel_id)},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Ошибка при запросе прогноза: %s", e)
        raise HTTPException(status_code=500, detail="Data interface forecast error")
