from abc import ABC, abstractmethod

from booking.application.ports.repositories import IHotelRepository, IBookingRepository, IOutboxEventRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def hotels(self) -> IHotelRepository:
        pass

    @property
    @abstractmethod
    def bookings(self) -> IBookingRepository:
        pass

    @property
    @abstractmethod
    def outbox(self) -> IOutboxEventRepository:
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
