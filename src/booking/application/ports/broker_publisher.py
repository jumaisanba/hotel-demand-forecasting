from abc import ABC, abstractmethod


class IMessageBrokerPublisher(ABC):
    """Интерфейс публикации событий в брокер."""

    @abstractmethod
    async def publish(
            self,
            *,
            routing_key: str,
            payload: dict,
            event_id: str,
            event_type: str,
    ) -> None:
        """Публикует событие в брокер."""
        raise NotImplementedError
