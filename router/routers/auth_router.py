# router/routers/auth_router.py

import logging
import requests
from fastapi import APIRouter, HTTPException

from router.config import AUTH_SERVICE_URL
from router.schemas import AuthRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login")
async def authorize_user(auth_req: AuthRequest):
    """
    Прокси для авторизации пользователя по API-ключу.
    Запрашивает токен у auth_service (/token/user).
    """
    try:
        headers = {"X-API-Key": auth_req.api_key}
        response = requests.post(f"{AUTH_SERVICE_URL}/token/user", headers=headers, timeout=5)
        response.raise_for_status()
        logger.info("Успешная авторизация")
        return response.json()
    except requests.RequestException as e:
        logger.error("Ошибка авторизации через auth_service: %s", e)
        raise HTTPException(status_code=401, detail="Authorization failed")


