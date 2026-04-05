from abc import ABC, abstractmethod

from auth.application.schemas.token import TokenRefreshPayload


class ITokenStorage(ABC):
    @abstractmethod
    async def store_token(self, payload: TokenRefreshPayload) -> None:
        """Сохранить refresh-токен."""
        raise NotImplementedError

    @abstractmethod
    async def revoke_token(self, jti: str, user_id: str) -> None:
        """Отозвать конкретный refresh-токен."""
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_tokens(self, user_id: str) -> None:
        """Отозвать все refresh-токены пользователя."""
        raise NotImplementedError

    @abstractmethod
    async def is_token_valid(self, jti: str) -> bool:
        """Проверить, существует ли refresh-токен."""
        raise NotImplementedError
