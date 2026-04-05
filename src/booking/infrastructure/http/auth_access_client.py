import httpx

from booking.config import booking_config


class AuthAccessClient:
    """HTTP-клиент для внутренних запросов в сервис авторизации."""

    def __init__(self, base_url: str, timeout: float = 5.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def assign_owner(self, user_id: int, hotel_id: int) -> None:
        """Назначает пользователя владельцем отеля через внутренний API auth-сервиса."""

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.post(
                "/internal/access/assign-owner",
                json={"user_id": user_id, "hotel_id": hotel_id},
            )
            resp.raise_for_status()


auth_access_client = AuthAccessClient(
    base_url=str(booking_config.auth_url),
    timeout=booking_config.auth_timeout_sec,
)
