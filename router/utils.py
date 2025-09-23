from typing import Dict

from fastapi import Header, HTTPException
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM
from routers.auth_router import logger


async def verify_token(authorization: str = Header(...)) -> Dict:
    """
    Локальная проверка JWT-токена.
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Декодированный токен: %s", payload)

        if "sub" not in payload or "role" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        if payload["role"] == "user" and "hotel_id" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return payload
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token verification failed")
