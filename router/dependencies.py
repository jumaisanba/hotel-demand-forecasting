import httpx
from typing import Dict
from fastapi import Header, HTTPException
from jose import jwt, JWTError

from router.config import SECRET_KEY, ALGORITHM


# --- HTTP client (singleton) ---
client: httpx.AsyncClient | None = None

async def get_http_client() -> httpx.AsyncClient:
    return client

async def startup_event():
    global client
    client = httpx.AsyncClient(timeout=10)

async def shutdown_event():
    global client
    if client:
        await client.aclose()


# --- JWT verification ---
def verify_token(authorization: str = Header(...)) -> Dict:
    """
    Проверка JWT-токена.
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if "sub" not in payload or "role" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        if payload["role"] == "user" and "hotel_id" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return payload
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token verification failed")
