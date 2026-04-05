from abc import ABC, abstractmethod

from auth.application.ports.repositories import IUserRepository, IUserHotelRepository, IProcessedEventRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def users(self) -> IUserRepository:
        pass

    @property
    @abstractmethod
    def users_hotels(self) -> IUserHotelRepository:
        pass

    @property
    @abstractmethod
    def processed_events(self) -> IProcessedEventRepository:
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
