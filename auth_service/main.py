import logging
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth_service.db import get_session, SCHEDULER_KEY
from auth_service.model_hotel_db import Hotel
from auth_service.utils import create_access_token

logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service API")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.get("/")
def root():
    return {"message": "AUTH_SERVICE работает!"}


@app.post("/token/system", response_model=TokenResponse)
def generate_system_token(
    x_system_key: str = Header(default=None)
):
    """
    Генерация токена для системного планировщика.
    """
    if not x_system_key or x_system_key != SCHEDULER_KEY:
        logger.warning("Неверная попытка авторизации системным ключом")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": "scheduler", "role": "scheduler"}
    token = create_access_token(payload)
    return TokenResponse(access_token=token)


@app.post("/token/user", response_model=TokenResponse)
def generate_user_token(
    x_api_key: str = Header(default=None),
    db: Session = Depends(get_session)
):
    """
    Генерация токена для отеля по API-ключу.
    """
    if not x_api_key:
        raise HTTPException(status_code=400, detail="API key required")

    hotel = db.query(Hotel).filter(Hotel.api_key == x_api_key).first()
    if not hotel:
        logger.warning("Попытка входа с неверным API ключом")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": str(hotel.id), "role": "user", "hotel_id": hotel.id}
    token = create_access_token(payload)

    logger.info("Сгенерирован токен для hotel_id=%s", hotel.id)
    return TokenResponse(access_token=token)
