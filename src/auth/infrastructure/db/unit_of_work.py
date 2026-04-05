from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.ports.unit_of_work import IUnitOfWork
from auth.infrastructure.db.repositories import (
    UserRepository,
    UserHotelRepository,
)
from auth.infrastructure.db.repositories.processed_event import ProcessedEventRepository
from shared.db import AsyncSessionLocal


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=AsyncSessionLocal):
        self._session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self._session_factory()
        self._users = UserRepository(self.session)
        self._users_hotels = UserHotelRepository(self.session)
        self._processed_events = ProcessedEventRepository(self.session)
        return self

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def users_hotels(self) -> UserHotelRepository:
        return self._users_hotels

    @property
    def processed_events(self) -> ProcessedEventRepository:
        return self._processed_events

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()

    async def rollback(self):
        await self.session.rollback()

    async def _commit(self):
        await self.session.commit()
