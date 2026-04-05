from sqlalchemy.ext.asyncio import AsyncSession

from booking.application.ports.unit_of_work import IUnitOfWork
from booking.infrastructure.db.repositories import HotelRepository
from booking.infrastructure.db.repositories.booking import BookingRepository
from booking.infrastructure.db.repositories.outbox_event import OutboxEventRepository
from shared.db import AsyncSessionLocal


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=AsyncSessionLocal):
        self._session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self._session_factory()
        self._hotels = HotelRepository(self.session)
        self._bookings = BookingRepository(self.session)
        self._outboxes = OutboxEventRepository(self.session)
        return self

    @property
    def hotels(self) -> HotelRepository:
        return self._hotels

    @property
    def bookings(self) -> BookingRepository:
        return self._bookings

    @property
    def outbox(self) -> OutboxEventRepository:
        return self._outboxes

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()

    async def rollback(self):
        await self.session.rollback()

    async def _commit(self):
        await self.session.commit()
