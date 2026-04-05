from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewOutboxEvent:
    """Данные для сохранения события в outbox."""

    id: str
    event_type: str
    routing_key: str
    payload: dict