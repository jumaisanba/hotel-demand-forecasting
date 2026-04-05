import logging

import aio_pika

logger = logging.getLogger(__name__)


class RabbitMQConnectionManager:
    """Управляет подключением к RabbitMQ."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._connection: aio_pika.RobustConnection | None = None

    async def get_connection(self) -> aio_pika.RobustConnection:
        """Возвращает активное подключение к RabbitMQ."""
        if self._connection is None or self._connection.is_closed:
            logger.info("Устанавливается подключение к RabbitMQ.")
            self._connection = await aio_pika.connect_robust(self._dsn)
            logger.info("Подключение к RabbitMQ установлено.")
        return self._connection

    async def close(self) -> None:
        """Закрывает подключение к RabbitMQ."""
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
            logger.info("Подключение к RabbitMQ закрыто.")
