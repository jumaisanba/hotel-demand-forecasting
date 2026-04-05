from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.unit_of_work import IUnitOfWork
from prediction.infrastructure.db.repositories.booking_projection import BookingProjectionRepository
from prediction.infrastructure.db.repositories.holiday import HolidayRepository
from prediction.infrastructure.db.repositories.hotel_projection import HotelProjectionRepository
from prediction.infrastructure.db.repositories.predictions import PredictionRepository
from prediction.infrastructure.db.repositories.weather import WeatherRepository
from shared.db import AsyncSessionLocal


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=AsyncSessionLocal):
        self._session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self._session_factory()
        self._bookings_projection = BookingProjectionRepository(self.session)
        self._holidays = HolidayRepository(self.session)
        self._hotels_projection = HotelProjectionRepository(self.session)
        self._prediction = PredictionRepository(self.session)
        self._weather = WeatherRepository(self.session)
        return self

    @property
    def bookings_projection(self) -> BookingProjectionRepository:
        return self._bookings_projection

    @property
    def holidays(self) -> HolidayRepository:
        return self._holidays

    @property
    def hotels_projection(self) -> HotelProjectionRepository:
        return self._hotels_projection

    @property
    def predictions(self) -> PredictionRepository:
        return self._prediction

    @property
    def weather(self) -> WeatherRepository:
        return self._weather

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()

    async def rollback(self):
        await self.session.rollback()

    async def _commit(self):
        await self.session.commit()
