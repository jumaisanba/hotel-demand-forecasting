from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.repositories import IHolidayRepository
from prediction.infrastructure.db.models import Holiday


class HolidayRepository(IHolidayRepository):
    """Репозиторий праздничных дней."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Holiday]:
        """Возвращает все праздничные дни."""
        stmt = select(Holiday).order_by(Holiday.day.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
