from abc import ABC, abstractmethod

from prediction.application.ports.repositories import IBookingProjectionRepository, IHotelProjectionRepository, \
    IHolidayRepository, IPredictionRepository, IWeatherRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def bookings_projection(self) -> IBookingProjectionRepository:
        pass

    @property
    @abstractmethod
    def holidays(self) -> IHolidayRepository:
        pass

    @property
    @abstractmethod
    def hotels_projection(self) -> IHotelProjectionRepository:
        pass

    @property
    @abstractmethod
    def predictions(self) -> IPredictionRepository:
        pass

    @property
    @abstractmethod
    def weather(self) -> IWeatherRepository:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def _commit(self):
        pass
