from abc import ABC, abstractmethod
from datetime import date

from booking.application.dto.booking.diff import ExistingBookingState
from booking.application.dto.booking.history import BookingDailyStats
from booking.application.dto.outbox import NewOutboxEvent
from booking.infrastructure.db.models import Hotel, Booking, OutboxEvent


class IHotelRepository(ABC):
    """Интерфейс доступа к данным отелей."""

    @abstractmethod
    async def create(self, name: str, is_city_hotel: bool, api_key: str, city_id: int = 1) -> Hotel | None:
        """Создаёт отель."""
        pass

    @abstractmethod
    async def get_by_id(self, hotel_id: int) -> Hotel | None:
        """Возвращает отель по id."""
        pass

    @abstractmethod
    async def get_by_api_key(self, api_key: str) -> Hotel | None:
        """Возвращает отель по API-ключу."""
        pass

    @abstractmethod
    async def exists_by_id(self, hotel_id: int) -> bool:
        """Проверяет существование отеля по id."""
        pass

    @abstractmethod
    async def exists_by_api_key(self, api_key: str) -> bool:
        """Проверяет существование API-ключа."""
        pass

    @abstractmethod
    async def update_api_key(self, hotel_id: int, new_api_key: str) -> Hotel | None:
        """Обновляет API-ключ отеля."""
        pass


class IBookingRepository(ABC):
    """Интерфейс доступа к данным бронирований."""

    @abstractmethod
    async def get_existing_state_by_refs(
            self,
            hotel_id: int,
            booking_refs: list[str]
    ) -> dict[str, ExistingBookingState]:
        """
        Возвращает состояние бронирований для сравнения.

        Используется для определения:
        - новые записи
        - изменённые
        - без изменений
        """
        pass

    @abstractmethod
    async def get_by_refs(
            self,
            hotel_id: int,
            booking_refs: list[str],
    ) -> dict[str, Booking]:
        """Возвращает ORM-модели бронирований по booking_ref."""
        pass

    @abstractmethod
    async def add(self, booking: Booking) -> None:
        """Добавляет одно бронирование."""
        pass

    @abstractmethod
    async def add_many(self, bookings: list[Booking]) -> None:
        """Добавляет несколько бронирований."""
        pass

    @abstractmethod
    async def get_daily_stats(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool | None = None,
    ) -> list[BookingDailyStats]:
        """Возвращает агрегированную статистику бронирований по дням."""
        pass


class IOutboxEventRepository(ABC):
    """Интерфейс репозитория outbox-событий."""

    @abstractmethod
    async def add(self, event: NewOutboxEvent) -> None:
        """Добавляет событие в outbox."""
        raise NotImplementedError

    @abstractmethod
    async def get_pending(self, limit: int) -> list[OutboxEvent]:
        """Возвращает пачку неподтверждённых событий."""
        raise NotImplementedError

    @abstractmethod
    async def mark_published(self, event_id: str) -> None:
        """Помечает событие как опубликованное."""
        raise NotImplementedError

    @abstractmethod
    async def mark_failed(self, event_id: str, error: str) -> None:
        """Помечает событие как неуспешное."""
        raise NotImplementedError
