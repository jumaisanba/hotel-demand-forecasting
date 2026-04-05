from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.repositories import IPredictionRepository
from prediction.infrastructure.db.models import Prediction


class PredictionRepository(IPredictionRepository):
    """Репозиторий прогнозов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, predictions: Sequence[Prediction]) -> None:
        """Сохраняет несколько прогнозов."""
        if predictions:
            self._session.add_all(predictions)

    async def get_by_hotel(
            self,
            hotel_id: int,
            date_from: date | None = None,
            date_to: date | None = None,
    ) -> Sequence[Prediction]:
        """Возвращает прогнозы по отелю."""
        stmt = (
            select(Prediction)
            .where(Prediction.hotel_id == hotel_id)
            .order_by(Prediction.target_date.asc())
        )

        if date_from is not None:
            stmt = stmt.where(Prediction.target_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(Prediction.target_date <= date_to)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_forecast_range(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool,
    ) -> list[Prediction]:
        """Возвращает прогноз по диапазону дат."""
        stmt = (
            select(Prediction)
            .where(Prediction.hotel_id == hotel_id)
            .where(Prediction.target_date >= date_from)
            .where(Prediction.target_date <= date_to)
            .where(Prediction.has_deposit == has_deposit)
            .order_by(Prediction.target_date.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
