from typing import Any

import pandas as pd

from booking.application.domain.booking_import import BookingImportSchema
from booking.application.dto.booking.parse import (
    BookingParseResult,
    ParsedBookingRow,
    RowParseError,
)
from booking.application.services.booking.date_parser import BookingDateParser
from shared.errors import ImportFormatError, MappingError


class BookingRowParser:
    """Преобразует подготовленные строки импорта в типизированные DTO."""

    def __init__(
            self,
            schema: BookingImportSchema,
            date_parser: BookingDateParser,
    ) -> None:
        self._schema = schema
        self._date_parser = date_parser

    def parse_many(self, df: pd.DataFrame) -> BookingParseResult:
        """
        Парсит все строки DataFrame.

        Успешно распарсенные строки попадают в parsed_rows,
        ошибки по строкам накапливаются в errors.
        """
        result = BookingParseResult()

        for row_number, row in enumerate(df.to_dict(orient="records"), start=2):
            try:
                result.parsed_rows.append(self.parse_row(row_number, row))
            except (MappingError, ImportFormatError) as exc:
                result.errors.append(
                    RowParseError(
                        row_number=row_number,
                        message=str(exc),
                    )
                )

        return result

    def parse_row(self, row_number: int, row: dict[str, Any]) -> ParsedBookingRow:
        """
        Парсит одну строку импорта в ParsedBookingRow.

        Ожидает, что DataFrame уже прошёл предобработку по схеме.
        """
        identity_field = self._schema.identity_field
        if identity_field is None:
            raise MappingError("В схеме не задано identity-поле.")

        booking_ref = self._normalize_identity(row.get(identity_field))

        arrival_date = self._date_parser.parse_date_field(row, field_name="arrival_date")
        if arrival_date is None:
            raise MappingError("Поле arrival_date должно быть заполнено.")

        source_updated_at = self._date_parser.parse_datetime_field(
            row,
            field_name="source_updated_at",
        )

        parsed_row = ParsedBookingRow(
            row_number=row_number,
            booking_ref=booking_ref,
            arrival_date=arrival_date,
            lead_time=self._require_int(row.get("lead_time"), field_name="lead_time"),
            adr=self._require_float(row.get("adr"), field_name="adr"),
            total_guests=self._require_int(row.get("total_guests"), field_name="total_guests"),
            total_nights=self._require_int(row.get("total_nights"), field_name="total_nights"),
            booking_changes=self._require_int(row.get("booking_changes"), field_name="booking_changes"),
            has_deposit=self._parse_has_deposit(row.get("has_deposit"), field_name="has_deposit"),
            is_cancellation=self._parse_bool_like(row.get("is_cancellation"), field_name="is_cancellation"),
            market_segment=self._require_str(row.get("market_segment"), field_name="market_segment"),
            distribution_channel=self._require_str(row.get("distribution_channel"), field_name="distribution_channel"),
            reserved_room_type=self._require_str(row.get("reserved_room_type"), field_name="reserved_room_type"),
            source_updated_at=source_updated_at,
        )

        self._validate_required_output_fields(parsed_row)
        return parsed_row

    def _validate_required_output_fields(self, row: ParsedBookingRow) -> None:
        """Проверяет, что обязательные выходные поля заполнены."""
        for field_name in self._schema.required_output_fields:
            value = getattr(row, field_name, None)

            if value is None:
                raise MappingError(
                    f"Обязательное выходное поле {field_name} не заполнено."
                )

            if isinstance(value, str) and not value.strip():
                raise MappingError(
                    f"Обязательное выходное поле {field_name} пустое."
                )

    @staticmethod
    def _normalize_identity(value: Any) -> str | None:
        """Нормализует значение identity-поля."""
        if value is None:
            return None

        normalized = str(value).strip()
        if not normalized:
            return None

        return normalized

    @staticmethod
    def _require_str(value: Any, *, field_name: str) -> str:
        if value is None:
            raise MappingError(f"Поле {field_name} пустое.")

        result = str(value).strip()
        if not result:
            raise MappingError(f"Поле {field_name} пустое.")

        return result

    @staticmethod
    def _require_int(value: Any, *, field_name: str) -> int:
        if value is None:
            raise MappingError(f"Поле {field_name} пустое.")

        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise MappingError(
                f"Некорректное целочисленное значение поля {field_name}: {value!r}"
            ) from exc

    @staticmethod
    def _require_float(value: Any, *, field_name: str) -> float:
        if value is None:
            raise MappingError(f"Поле {field_name} пустое.")

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise MappingError(
                f"Некорректное вещественное значение поля {field_name}: {value!r}"
            ) from exc

    @staticmethod
    def _parse_bool_like(value: Any, *, field_name: str) -> bool:
        """Преобразует bool-like значение в bool."""
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return bool(value)

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y"}:
                return True
            if normalized in {"false", "0", "no", "n"}:
                return False

        raise MappingError(
            f"Некорректное булево значение поля {field_name}: {value!r}"
        )

    @staticmethod
    def _parse_has_deposit(value: Any, *, field_name: str) -> bool:
        """
        Преобразует поле has_deposit в bool.

        Текущая бизнес-логика:
        - None -> False
        - bool -> как есть
        - 'No Deposit' -> False
        - всё остальное -> True
        """
        if value is None:
            raise MappingError(f"Поле {field_name} пустое.")

        if isinstance(value, bool):
            return value

        normalized = str(value).strip().lower()
        return normalized != "no deposit"
