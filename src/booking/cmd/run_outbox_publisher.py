import asyncio
import logging

from booking.config import booking_config
from booking.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from booking.infrastructure.messaging.outbox_publisher import OutboxPublisherService
from booking.infrastructure.messaging.rabbitmq_connection import RabbitMQConnectionManager
from booking.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Периодически публикует события из outbox."""
    connection_manager = RabbitMQConnectionManager(booking_config.rabbitmq.dsn)
    connection = await connection_manager.get_connection()

    publisher = RabbitMQPublisher(connection=connection)

    service = OutboxPublisherService(
        uow_factory=SQLAlchemyUnitOfWork,
        broker_publisher=publisher,
        batch_size=booking_config.outbox_batch_size,
    )

    logger.info("Процесс публикации outbox-событий запущен.")

    while True:
        published = await service.publish_pending()
        if published:
            logger.info("Опубликовано outbox-событий: %s", published)
        await asyncio.sleep(booking_config.outbox_publish_interval_sec)


if __name__ == "__main__":
    asyncio.run(main())