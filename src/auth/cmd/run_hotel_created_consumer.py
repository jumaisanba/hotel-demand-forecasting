import asyncio
import logging

from auth.application.event_handlers.hotel_created import HotelCreatedEventHandler
from auth.config import auth_config
from auth.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from auth.infrastructure.messaging.hotel_created_consumer import HotelCreatedConsumer
from auth.infrastructure.messaging.rabbitmq_connection import RabbitMQConnectionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    connection_manager = RabbitMQConnectionManager(auth_config.rabbitmq.dsn)
    connection = await connection_manager.get_connection()

    handler = HotelCreatedEventHandler(
        uow=SQLAlchemyUnitOfWork(),
    )

    consumer = HotelCreatedConsumer(
        connection=connection,
        handler=handler,
    )

    await consumer.start()

    logger.info("Процесс consumer запущен.")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
