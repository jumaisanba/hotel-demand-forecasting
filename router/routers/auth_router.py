import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends

from router.config import AUTH_SERVICE_URL
from router.schemas import AuthRequest
from router.dependencies import get_http_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login")
async def authorize_user(
    auth_req: AuthRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Прокси для авторизации пользователя по API-ключу.
    Запрашивает токен у auth_service (/token/user).
    """
    headers = {"X-API-Key": auth_req.api_key}

    try:
        response = await client.post(f"{AUTH_SERVICE_URL}/token/user", headers=headers)
        response.raise_for_status()
        logger.info("Успешная авторизация")
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("auth_service вернул ошибку: %s", e)
        raise HTTPException(status_code=e.response.status_code, detail="Authorization failed")
    except httpx.RequestError as e:
        logger.error("Ошибка соединения с сервисом авторизации: %s", e)
        raise HTTPException(status_code=502, detail="Auth service connection error")
