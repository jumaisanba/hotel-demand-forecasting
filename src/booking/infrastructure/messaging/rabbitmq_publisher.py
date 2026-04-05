import json

import aio_pika

from booking.application.ports.broker_publisher import IMessageBrokerPublisher


class RabbitMQPublisher(IMessageBrokerPublisher):
    """Отправляет события в RabbitMQ."""

    def __init__(
            self,
            connection: aio_pika.RobustConnection,
            exchange_name: str = "booking.events",
    ) -> None:
        self._connection = connection
        self._exchange_name = exchange_name

    async def publish(
            self,
            *,
            routing_key: str,
            payload: dict,
            event_id: str,
            event_type: str,
    ) -> None:
        channel = await self._connection.channel()
        exchange = await channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=event_id,
                type=event_type,
            ),
            routing_key=routing_key,
        )
