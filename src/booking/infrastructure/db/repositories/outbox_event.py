from datetime import datetime, UTC

from sqlalchemy import select, update

from booking.application.dto.outbox import NewOutboxEvent
from booking.application.ports.repositories import IOutboxEventRepository
from booking.infrastructure.db.models import OutboxEvent


class OutboxEventRepository(IOutboxEventRepository):
    """Репозиторий outbox-событий."""

    def __init__(self, session):
        self._session = session

    async def add(self, event: NewOutboxEvent) -> None:
        """Сохраняет событие в outbox."""
        self._session.add(
            OutboxEvent(
                id=event.id,
                event_type=event.event_type,
                routing_key=event.routing_key,
                payload=event.payload,
            )
        )

    async def get_pending(self, limit: int) -> list[OutboxEvent]:
        """Возвращает пачку событий со статусом pending."""
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.status == "pending")
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def mark_published(self, event_id: str) -> None:
        """Помечает событие как опубликованное."""
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status="published",
                published_at=datetime.now(UTC),
                last_error=None,
            )
        )
        await self._session.execute(stmt)

    async def mark_failed(self, event_id: str, error: str) -> None:
        """Помечает событие как failed."""
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status="failed",
                last_error=error[:2000],
            )
        )
        await self._session.execute(stmt)
