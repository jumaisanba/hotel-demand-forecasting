import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from auth.application.event_handlers.hotel_created import HotelCreatedEventHandler
from auth.application.schemas.roles import UserRole

logger = logging.getLogger(__name__)


class HotelCreatedConsumer:
    """Консьюмер события hotel.created."""

    def __init__(
            self,
            connection: aio_pika.RobustConnection,
            handler: HotelCreatedEventHandler,
            queue_name: str = "auth.hotel-created",
            exchange_name: str = "booking.events",
            routing_key: str = "hotel.created",
    ) -> None:
        self._connection = connection
        self._handler = handler
        self._queue_name = queue_name
        self._exchange_name = exchange_name
        self._routing_key = routing_key

    async def start(self) -> None:
        """Запускает подписку на очередь RabbitMQ."""
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        queue = await channel.declare_queue(
            self._queue_name,
            durable=True,
        )
        await queue.bind(exchange, routing_key=self._routing_key)
        await queue.consume(self._handle_message)

        logger.info(
            "Консьюмер hotel.created запущен: queue=%s, exchange=%s, routing_key=%s",
            self._queue_name,
            self._exchange_name,
            self._routing_key,
        )

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        """Обрабатывает одно сообщение из очереди."""
        async with message.process():
            payload = json.loads(message.body.decode("utf-8"))

            logger.info(
                "Получено событие hotel.created: event_id=%s, hotel_id=%s, owner_user_id=%s",
                payload.get("event_id"),
                payload.get("hotel_id"),
                payload.get("owner_user_id"),
            )

            await self._handler.handle(
                event_id=payload["event_id"],
                hotel_id=payload["hotel_id"],
                owner_user_id=payload["owner_user_id"],
                role=UserRole(payload.get("role", "owner")),
            )
