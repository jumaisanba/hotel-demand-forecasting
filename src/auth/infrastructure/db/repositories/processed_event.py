from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.ports.repositories import IProcessedEventRepository
from auth.infrastructure.db.models import ProcessedEvent


class ProcessedEventRepository(IProcessedEventRepository):
    """Репозиторий обработанных событий."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def exists(self, event_id: str) -> bool:
        """Проверяет, было ли событие уже обработано."""
        stmt = select(
            exists().where(ProcessedEvent.event_id == event_id)
        )
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def add(self, event_id: str, event_type: str) -> None:
        """Сохраняет факт обработки события."""
        self._session.add(
            ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
            )
        )