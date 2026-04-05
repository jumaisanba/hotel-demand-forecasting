from abc import ABC, abstractmethod
from typing import Sequence

from auth.application.schemas.roles import SystemRole, UserRole
from auth.infrastructure.db.models import User, UserHotel


class IUserRepository(ABC):
    @abstractmethod
    async def create(
            self,
            name: str,
            surname: str,
            email: str,
            hashed_password: str,
            system_role: SystemRole = SystemRole.USER.value,
            is_active: bool = True,
    ) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def exists_by_id(self, user_id: int) -> bool:
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    async def update_password(self, user_id: int, hashed_password: str) -> User | None:
        pass

    @abstractmethod
    async def deactivate(self, user_id: int) -> User | None:
        pass


class IUserHotelRepository(ABC):
    @abstractmethod
    async def create(self, user_id: int, hotel_id: int, role: UserRole) -> UserHotel:
        pass

    @abstractmethod
    async def get(self, user_id: int, hotel_id: int) -> UserHotel | None:
        pass

    @abstractmethod
    async def get_hotels_by_user(self, user_id: int) -> Sequence[UserHotel]:
        pass

    @abstractmethod
    async def get_users_by_hotel(self, hotel_id: int) -> Sequence[UserHotel]:
        pass

    @abstractmethod
    async def update_role(self, user_id: int, hotel_id: int, role: UserRole) -> UserHotel | None:
        pass


class IProcessedEventRepository(ABC):
    """Интерфейс репозитория обработанных событий."""

    @abstractmethod
    async def exists(self, event_id: str) -> bool:
        """Проверяет, было ли событие уже обработано."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, event_id: str, event_type: str) -> None:
        """Сохраняет факт обработки события."""
        raise NotImplementedError