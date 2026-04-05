from __future__ import annotations

from datetime import date, datetime
from typing import Any

from dateutil.parser import parse

from booking.application.domain.booking_import import DerivedFieldRule, BookingImportSchema
from shared.errors import ImportFormatError

RUS_MONTH_MAP = {
    "январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5, "июнь": 6,
    "июль": 7, "август": 8, "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12,
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "июн": 6,
    "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12,
}

EN_MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9,
    "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

SUPPORTED_DATE_FORMATS = (
    "%d.%m.%Y",
    "%d.%m.%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y-%m-%d",
)


class BookingDateParser:
    """Парсит date/datetime-поля строки импорта по правилам схемы."""

    def __init__(self, schema: BookingImportSchema) -> None:
        self._schema = schema

    def parse_field(
            self,
            row: dict[str, Any],
            *,
            field_name: str,
    ) -> date | datetime | None:
        """
        Парсит temporal-поле по имени.

        Поддерживает:
        - обычные date/datetime поля;
        - derived date-поля, собираемые из альтернативных источников.
        """
        field_rule = self._schema.field_map.get(field_name)
        if field_rule is None:
            raise ImportFormatError(f"Поле {field_name} не описано в схеме.")

        if field_rule.semantic == "plain":
            raise ImportFormatError(
                f"Поле {field_name} не является temporal-полем."
            )

        derived_rule = self._schema.derived_map.get(field_name)

        if field_rule.semantic == "date":
            if derived_rule is not None:
                return self._parse_derived_date(
                    row=row,
                    rule=derived_rule,
                    target=field_name,
                    nullable=field_rule.nullable,
                )
            return self._parse_single_date(
                value=row.get(field_name),
                field_name=field_name,
                nullable=field_rule.nullable,
            )

        if field_rule.semantic == "datetime":
            if derived_rule is not None:
                raise ImportFormatError(
                    f"Derived datetime-поля пока не поддерживаются: {field_name}."
                )
            return self._parse_single_datetime(
                value=row.get(field_name),
                field_name=field_name,
                nullable=field_rule.nullable,
            )

        raise ImportFormatError(
            f"Неизвестная semantic для поля {field_name}: {field_rule.semantic!r}"
        )

    def parse_date_field(
            self,
            row: dict[str, Any],
            *,
            field_name: str,
    ) -> date | None:
        """Парсит поле и гарантирует, что результат имеет тип date."""
        value = self.parse_field(row, field_name=field_name)

        if value is None:
            return None

        if isinstance(value, datetime):
            raise ImportFormatError(
                f"Поле {field_name} распарсилось как datetime, ожидалась date."
            )

        if not isinstance(value, date):
            raise ImportFormatError(
                f"Поле {field_name} не распарсилось как date."
            )

        return value

    def parse_datetime_field(
            self,
            row: dict[str, Any],
            *,
            field_name: str,
    ) -> datetime | None:
        """Парсит поле и гарантирует, что результат имеет тип datetime."""
        value = self.parse_field(row, field_name=field_name)

        if value is None:
            return None

        if not isinstance(value, datetime):
            raise ImportFormatError(
                f"Поле {field_name} не распарсилось как datetime."
            )

        return value

    def _parse_single_date(
            self,
            *,
            value: Any,
            field_name: str,
            nullable: bool,
    ) -> date | None:
        """Парсит одиночное date-значение."""
        if not self._has_value(value):
            if nullable:
                return None
            raise ImportFormatError(f"Поле {field_name} пустое.")

        return self._parse_date_value(value, field_name=field_name)

    def _parse_single_datetime(
            self,
            *,
            value: Any,
            field_name: str,
            nullable: bool,
    ) -> datetime | None:
        """Парсит одиночное datetime-значение."""
        if not self._has_value(value):
            if nullable:
                return None
            raise ImportFormatError(f"Поле {field_name} пустое.")

        return self._parse_datetime_value(value, field_name=field_name)

    def _parse_derived_date(
            self,
            *,
            row: dict[str, Any],
            rule: DerivedFieldRule,
            target: str,
            nullable: bool,
    ) -> date | None:
        """
        Собирает дату из одного из допустимых наборов полей.

        Например:
        - напрямую из `arrival_date`;
        - из `year + month + day`.
        """
        resolved_dates: list[date] = []

        for source_group in rule.sources_any_of:
            if len(source_group) == 1:
                value = row.get(source_group[0])
                if self._has_value(value):
                    resolved_dates.append(
                        self._parse_date_value(value, field_name=target)
                    )
                continue

            if len(source_group) == 3:
                year_field, month_field, day_field = source_group
                year = row.get(year_field)
                month = row.get(month_field)
                day = row.get(day_field)

                if all(self._has_value(v) for v in (year, month, day)):
                    resolved_dates.append(
                        self._parse_composed_date(
                            year=year,
                            month=month,
                            day=day,
                            field_name=target,
                        )
                    )
                continue

            raise ImportFormatError(
                f"Некорректная конфигурация derived-поля {target}: {source_group!r}"
            )

        if not resolved_dates:
            if nullable:
                return None
            raise ImportFormatError(
                f"Не удалось собрать поле {target}: нет валидного источника."
            )

        if rule.conflict_policy == "first_valid":
            return resolved_dates[0]

        if rule.conflict_policy == "error_on_conflict":
            first = resolved_dates[0]
            if any(value != first for value in resolved_dates[1:]):
                raise ImportFormatError(
                    f"Конфликт значений для derived-поля {target}."
                )
            return first

        raise ImportFormatError(
            f"Неизвестная conflict_policy для поля {target}: {rule.conflict_policy!r}"
        )

    def _parse_date_value(
            self,
            value: Any,
            *,
            field_name: str,
    ) -> date:
        """Преобразует произвольное значение в date."""
        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        if isinstance(value, datetime):
            return value.date()

        raw_value = self._normalize_string(value)
        if raw_value is None:
            raise ImportFormatError(f"Поле {field_name} пустое.")

        for fmt in SUPPORTED_DATE_FORMATS:
            try:
                return datetime.strptime(raw_value, fmt).date()
            except ValueError:
                continue

        try:
            return parse(raw_value, dayfirst=True, fuzzy=False).date()
        except (ValueError, OverflowError) as exc:
            raise ImportFormatError(
                f"Не удалось распарсить дату в поле {field_name}: '{raw_value}'."
            ) from exc

    def _parse_datetime_value(
            self,
            value: Any,
            *,
            field_name: str,
    ) -> datetime:
        """Преобразует произвольное значение в date."""
        if isinstance(value, datetime):
            return value

        raw_value = self._normalize_string(value)
        if raw_value is None:
            raise ImportFormatError(f"Поле {field_name} пустое.")

        try:
            return parse(raw_value, dayfirst=True, fuzzy=False)
        except (ValueError, OverflowError) as exc:
            raise ImportFormatError(
                f"Не удалось распарсить datetime в поле {field_name}: '{raw_value}'."
            ) from exc

    def _parse_composed_date(
            self,
            *,
            year: Any,
            month: Any,
            day: Any,
            field_name: str,
    ) -> date:
        """Собирает дату из составных полей year/month/day."""
        parsed_year = self._normalize_year(year)
        parsed_month = self._normalize_month(month)
        parsed_day = self._normalize_day(day)

        try:
            return date(parsed_year, parsed_month, parsed_day)
        except ValueError as exc:
            raise ImportFormatError(
                f"Некорректная составная дата для поля {field_name}: "
                f"year={parsed_year}, month={parsed_month}, day={parsed_day}."
            ) from exc

    @staticmethod
    def _normalize_string(value: Any) -> str | None:
        """Преобразует значение в непустую строку или None."""
        if value is None:
            return None

        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None

        return str(value).strip() or None

    @classmethod
    def _has_value(cls, value: Any) -> bool:
        """Проверяет, что значение не пустое после нормализации."""
        return cls._normalize_string(value) is not None

    @classmethod
    def _normalize_int_part(cls, value: Any, *, field_name: str) -> int:
        """Преобразует часть составной даты в целое число."""
        normalized = cls._normalize_string(value)
        if normalized is None:
            raise ImportFormatError(f"{field_name} пустой.")

        try:
            return int(normalized)
        except ValueError as exc:
            raise ImportFormatError(f"Некорректное значение поля {field_name}: '{value}'.") from exc

    @classmethod
    def _normalize_year(cls, value: Any) -> int:
        """Нормализует год составной даты."""
        return cls._normalize_int_part(value, field_name="Год даты")

    @classmethod
    def _normalize_day(cls, value: Any) -> int:
        """Нормализует день составной даты."""
        return cls._normalize_int_part(value, field_name="День даты")

    @classmethod
    def _normalize_month(cls, value: Any) -> int:
        """Преобразует месяц в номер с поддержкой RU/EN названий."""
        if isinstance(value, int):
            return value

        if isinstance(value, float) and value.is_integer():
            return int(value)

        normalized = cls._normalize_string(value)
        if normalized is None:
            raise ImportFormatError("Месяц даты пустой.")

        lowered = normalized.lower()

        if lowered in RUS_MONTH_MAP:
            return RUS_MONTH_MAP[lowered]

        if lowered in EN_MONTH_MAP:
            return EN_MONTH_MAP[lowered]

        if lowered.isdigit():
            return int(lowered)

        raise ImportFormatError(f"Неизвестный месяц: '{value}'.")
