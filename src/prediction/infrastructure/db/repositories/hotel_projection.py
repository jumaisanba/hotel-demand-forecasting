from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.repositories import IHotelProjectionRepository
from prediction.infrastructure.db.models import HotelProjection


class HotelProjectionRepository(IHotelProjectionRepository):
    """Репозиторий проекции отелей."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, hotel_id: int) -> HotelProjection | None:
        """Возвращает проекцию отеля по id."""
        stmt = select(HotelProjection).where(HotelProjection.id == hotel_id)
        return await self._session.scalar(stmt)

    async def upsert(self, hotel: HotelProjection) -> None:
        """Создаёт или обновляет проекцию отеля."""
        stmt = insert(HotelProjection).values(
            id=hotel.id,
            city_id=hotel.city_id,
            is_city_hotel=hotel.is_city_hotel,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "city_id": stmt.excluded.city_id,
                "is_city_hotel": stmt.excluded.is_city_hotel,
            },
        )

        await self._session.execute(stmt)
