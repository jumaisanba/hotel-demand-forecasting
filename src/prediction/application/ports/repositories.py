from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date

from prediction.infrastructure.db.models import (
    BookingProjection,
    Holiday,
    Prediction,
    Weather,
    HotelProjection,
)


class IBookingProjectionRepository(ABC):
    """Интерфейс репозитория проекции бронирований."""

    @abstractmethod
    async def get_by_hotel(self, hotel_id: int) -> Sequence[BookingProjection]:
        """Возвращает проекцию бронирований по отелю."""
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, booking: BookingProjection) -> None:
        """Создаёт или обновляет запись проекции бронирования."""
        raise NotImplementedError

    @abstractmethod
    async def get_history_summary(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool,
    ) -> Sequence[object]:
        """Возвращает агрегированную историю бронирований по дням."""
        raise NotImplementedError


class IHotelProjectionRepository(ABC):
    """Интерфейс репозитория проекции отелей."""

    @abstractmethod
    async def get_by_id(self, hotel_id: int) -> HotelProjection | None:
        """Возвращает проекцию отеля по id."""
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, hotel: HotelProjection) -> None:
        """Создаёт или обновляет проекцию отеля."""
        raise NotImplementedError


class IWeatherRepository(ABC):
    """Интерфейс репозитория погодных данных."""

    @abstractmethod
    async def get_by_city(self, city_id: int) -> Sequence[Weather]:
        """Возвращает погодные данные по городу."""
        raise NotImplementedError


class IHolidayRepository(ABC):
    """Интерфейс репозитория праздничных дней."""

    @abstractmethod
    async def list_all(self) -> Sequence[Holiday]:
        """Возвращает все праздничные дни."""
        raise NotImplementedError


class IPredictionRepository(ABC):
    """Интерфейс репозитория прогнозов."""

    @abstractmethod
    async def add_many(self, predictions: Sequence[Prediction]) -> None:
        """Сохраняет несколько прогнозов."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_hotel(
            self,
            hotel_id: int,
            date_from: date | None = None,
            date_to: date | None = None,
    ) -> Sequence[Prediction]:
        """Возвращает прогнозы по отелю."""
        raise NotImplementedError

    @abstractmethod
    async def get_forecast_range(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool,
    ) -> Sequence[object]:
        """Возвращает прогноз по диапазону дат."""
        raise NotImplementedError
