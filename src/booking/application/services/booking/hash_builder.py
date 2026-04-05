import hashlib
from datetime import date, datetime
from typing import Any, Callable

from booking.application.domain.booking_import import BookingImportSchema
from booking.application.dto.booking.parse import ParsedBookingRow


class BookingHashBuilder:
    """Строит payload_hash для строки бронирования."""

    def __init__(self, schema: BookingImportSchema) -> None:
        if not schema.hash_fields:
            raise ValueError("В BookingImportSchema не заданы hash_fields.")
        self._hash_fields = schema.hash_fields

    def build_from_parsed_row(self, row: ParsedBookingRow) -> str:
        """Строит хеш из полей ParsedBookingRow."""
        return self._build(lambda field: getattr(row, field))

    def build_from_mapping(self, data: dict[str, Any]) -> str:
        """Строит хеш из словаря значений."""
        return self._build(lambda field: data.get(field))

    def _build(self, getter: Callable[[str], Any]) -> str:
        """Собирает строку по hash_fields и вычисляет SHA-256."""
        payload = "|".join(
            self._normalize_value(getter(field))
            for field in self._hash_fields
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_value(value: Any) -> str:
        """Приводит значение к стабильному строковому виду для хеширования."""
        if value is None:
            return "<NULL>"

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, float):
            return f"{value:.6f}"

        return str(value).strip()
