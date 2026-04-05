import logging
from typing import Callable

from booking.application.ports.broker_publisher import IMessageBrokerPublisher
from booking.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class OutboxPublisherService:
    """Публикует pending-события из outbox в RabbitMQ."""

    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
            broker_publisher: IMessageBrokerPublisher,
            batch_size: int = 100,
    ) -> None:
        self._uow_factory = uow_factory
        self._broker_publisher = broker_publisher
        self._batch_size = batch_size

    async def publish_pending(self) -> int:
        """Публикует одну пачку pending-событий."""
        async with self._uow_factory() as uow:
            events = await uow.outbox.get_pending(limit=self._batch_size)

            if not events:
                return 0

            published_count = 0

            for event in events:
                try:
                    await self._broker_publisher.publish(
                        routing_key=event.routing_key,
                        payload=event.payload,
                        event_id=event.id,
                        event_type=event.event_type,
                    )
                    await uow.outbox.mark_published(event.id)
                    published_count += 1
                except Exception as exc:
                    logger.exception(
                        "Не удалось опубликовать outbox-событие: event_id=%s, event_type=%s",
                        event.id,
                        event.event_type,
                    )
                    await uow.outbox.mark_failed(event.id, str(exc))

            await uow.commit()
            return published_count
