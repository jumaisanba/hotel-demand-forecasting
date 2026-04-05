from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.repositories import IWeatherRepository
from prediction.infrastructure.db.models import Weather


class WeatherRepository(IWeatherRepository):
    """Репозиторий погодных данных."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_city(self, city_id: int) -> Sequence[Weather]:
        """Возвращает погодные данные по городу."""
        stmt = (
            select(Weather)
            .where(Weather.city_id == city_id)
            .order_by(Weather.day.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
