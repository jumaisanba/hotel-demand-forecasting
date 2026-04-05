import logging

import pandas as pd

from booking.application.domain.booking_import import (
    BookingImportSchema,
    ImportFieldRule, DerivedFieldRule,
)
from shared.errors import ImportFormatError

logger = logging.getLogger(__name__)


class BookingDataFramePreprocessor:
    """Подготавливает DataFrame с бронированиями к дальнейшей обработке."""

    def __init__(self, schema: BookingImportSchema):
        self._schema = schema

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Полный пайплайн предобработки:
        нормализация имен колонок → алиасы → обязательная структура → нормализация значений → агрегаты.
        """
        prepared_df = df.copy()

        prepared_df = self._normalize_raw_column_names(prepared_df)
        prepared_df = self._apply_aliases(prepared_df)
        self._validate_required_structure(prepared_df)
        prepared_df = self._normalize_fields(prepared_df)
        prepared_df = self._compute_aggregates(prepared_df)

        logger.debug(
            "DataFrame бронирований подготовлен: строк=%s, колонок=%s",
            prepared_df.shape[0],
            prepared_df.shape[1],
        )
        return prepared_df

    def _apply_aliases(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Переименовывает колонки по алиасам в канонические имена.

        Если найдено несколько алиасов одного поля, используется первый.
        """
        aliased_df = df.copy()
        rename_map: dict[str, str] = {}

        for field in self._schema.fields:
            matched_aliases = [
                alias for alias in field.aliases if alias in aliased_df.columns
            ]
            if not matched_aliases:
                continue

            if len(matched_aliases) > 1:
                logger.warning(
                    "Найдено несколько алиасов для колонки %r: %s. "
                    "Будет использована колонка %r.",
                    field.canonical_name,
                    matched_aliases,
                    matched_aliases[0],
                )

            rename_map[matched_aliases[0]] = field.canonical_name

        return aliased_df.rename(columns=rename_map)

    def _validate_required_structure(self, df: pd.DataFrame) -> None:
        """
        Проверяет наличие обязательных колонок и допустимых групп для derived-полей.
        """
        available_columns = set(df.columns)

        missing_required = [
            field_name
            for field_name in self._schema.required_input_fields
            if field_name not in available_columns
        ]
        if missing_required:
            raise ImportFormatError(
                "Отсутствуют обязательные колонки: "
                f"{', '.join(sorted(missing_required))}."
            )

        for rule in self._schema.derived_fields:
            if not self._has_any_derived_source(available_columns, rule):
                readable_sources = " или ".join(
                    f"[{', '.join(group)}]" for group in rule.sources_any_of
                )
                raise ImportFormatError(
                    f"Невозможно получить поле '{rule.target}'. "
                    f"Ожидается один из наборов колонок: {readable_sources}."
                )

    def _normalize_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Нормализует поля по схеме:
        - создаёт отсутствующие колонки с default;
        - очищает и приводит значения по kind;
        - применяет strip для строковых полей при необходимости.
        """
        normalized_df = df.copy()

        for field in self._schema.fields:
            if field.canonical_name not in normalized_df.columns:
                if field.default is None:
                    continue
                normalized_df[field.canonical_name] = pd.Series(
                    [field.default] * len(normalized_df),
                    index=normalized_df.index,
                )
                continue

            normalized_df[field.canonical_name] = self._normalize_series(
                normalized_df[field.canonical_name],
                field,
            )

        return normalized_df

    def _normalize_series(
            self,
            series: pd.Series,
            field: ImportFieldRule
    ) -> pd.Series:
        """Нормализует одну колонку в соответствии с типом поля."""
        if field.kind == "int":
            return self._clean_numeric_series(
                series=series,
                default=field.default if field.default is not None else 0,
                dtype=int,
            )

        if field.kind == "float":
            return self._clean_numeric_series(
                series=series,
                default=field.default if field.default is not None else 0.0,
                dtype=float,
            )

        if field.kind in {"string", "bool_like", "date_part"}:
            return self._clean_string_like_series(series, field)

        return series

    def _clean_string_like_series(
            self,
            series: pd.Series,
            field: ImportFieldRule,
    ) -> pd.Series:
        """
        Нормализует строкоподобную колонку:
        - при необходимости подставляет default;
        - применяет strip;
        - пустые значения оставляет как None для nullable-полей.
        """
        normalized = series.copy()

        if field.default is not None:
            normalized = normalized.fillna(field.default)

        normalized = normalized.map(self._normalize_scalar_string_like)

        if field.strip:
            normalized = normalized.map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

        normalized = normalized.map(
            lambda value: None if isinstance(value, str) and value == "" else value
        )

        if field.default is not None:
            normalized = normalized.fillna(field.default)

        if not field.nullable and field.default is not None:
            normalized = normalized.fillna(field.default)

        return normalized

    def _compute_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Вычисляет агрегированные поля с учетом policy:
        - prefer_target
        - recompute
        - error_on_conflict
        """
        computed_df = df.copy()

        for aggregate in self._schema.aggregates:
            sum_series = (
                computed_df[list(aggregate.sources)]
                .sum(axis=1, min_count=1)
                .fillna(0)
            )

            if aggregate.target not in computed_df.columns:
                computed_df[aggregate.target] = sum_series
                continue

            if aggregate.policy == "recompute":
                computed_df[aggregate.target] = sum_series
                continue

            if aggregate.policy == "prefer_target":
                target_series = pd.to_numeric(
                    computed_df[aggregate.target],
                    errors="coerce",
                ).fillna(0)

                mask = target_series <= 0
                computed_df.loc[mask, aggregate.target] = sum_series[mask]
                continue

            if aggregate.policy == "error_on_conflict":
                target_series = pd.to_numeric(
                    computed_df[aggregate.target],
                    errors="coerce",
                ).fillna(0)

                conflict_mask = target_series.ne(sum_series)
                if conflict_mask.any():
                    raise ImportFormatError(
                        f"Конфликт агрегированного поля '{aggregate.target}'."
                    )
                continue

            raise ImportFormatError(
                f"Неизвестная aggregate policy для поля '{aggregate.target}': "
                f"{aggregate.policy!r}."
            )

        return computed_df

    @staticmethod
    def _has_any_derived_source(
            available_columns: set[str],
            rule: DerivedFieldRule
    ) -> bool:
        """Проверяет, что для производного поля доступен хотя бы один набор источников."""
        return any(
            set(source_group).issubset(available_columns)
            for source_group in rule.sources_any_of
        )

    @staticmethod
    def _normalize_raw_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Приводит имена колонок к виду: lower + strip + snake_case."""
        normalized_df = df.copy()
        normalized_df.columns = (
            normalized_df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )
        return normalized_df

    @staticmethod
    def _normalize_scalar_string_like(value: object) -> object:
        """
        Нормализует одно строкоподобное значение.

        Пустые и служебные значения (`None`, `NULL`, `NaN`, `N/A`) приводит к None.
        """
        if value is None:
            return None

        if isinstance(value, str):
            stripped = value.strip()
            if stripped in {"", "None", "none", "NULL", "null", "NaN", "nan", "N/A", "n/a"}:
                return None
            return stripped

        text = str(value).strip()
        if text in {"", "None", "none", "NULL", "null", "NaN", "nan", "N/A", "n/a"}:
            return None

        return text

    @staticmethod
    def _clean_numeric_series(
            series: pd.Series,
            default: int | float,
            dtype: type[int] | type[float],
    ) -> pd.Series:
        """
        Нормализует числовую колонку:
        - очищает пустые и мусорные значения;
        - преобразует в число;
        - заполняет пропуски default;
        - приводит к нужному типу.
        """
        cleaned = series.astype(str).str.strip()

        bad_values = ("", "None", "none", "NULL", "null", "NaN", "nan", "N/A", "n/a")
        cleaned = cleaned.replace(list(bad_values), str(default))
        cleaned = cleaned.replace(r"^\s*$", str(default), regex=True)

        numeric = pd.to_numeric(cleaned, errors="coerce")
        numeric = numeric.fillna(default)

        return numeric.astype(dtype)
