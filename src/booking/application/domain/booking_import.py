from dataclasses import dataclass
from functools import cached_property
from typing import Any, Literal

PreprocessKind = Literal["string", "int", "float", "bool_like", "date_part"]
FieldSemantic = Literal["plain", "date", "datetime"]

DerivedConflictPolicy = Literal["first_valid", "error_on_conflict"]
AggregatePolicy = Literal["prefer_target", "recompute", "error_on_conflict"]


@dataclass(frozen=True)
class ImportFieldRule:
    """Правило нормализации входного поля (парсинг + предобработка)."""

    canonical_name: str
    aliases: tuple[str, ...] = ()
    default: Any = None
    kind: PreprocessKind = "string"
    strip: bool = False
    semantic: FieldSemantic = "plain"
    nullable: bool = True
    is_identity: bool = False


@dataclass(frozen=True)
class AggregateRule:
    """Правило агрегации нескольких полей в одно (например total_guests)."""

    target: str
    sources: tuple[str, ...]
    policy: AggregatePolicy = "prefer_target"


@dataclass(frozen=True)
class DerivedFieldRule:
    """Правило вычисления поля из альтернативных наборов источников."""

    target: str
    sources_any_of: tuple[tuple[str, ...], ...]
    conflict_policy: DerivedConflictPolicy = "first_valid"


@dataclass(frozen=True)
class BookingImportSchema:
    """Схема импорта бронирований."""

    fields: tuple[ImportFieldRule, ...]
    required_input_fields: tuple[str, ...] = ()
    required_output_fields: tuple[str, ...] = ()
    derived_fields: tuple[DerivedFieldRule, ...] = ()
    aggregates: tuple[AggregateRule, ...] = ()
    hash_fields: tuple[str, ...] = ()

    @cached_property
    def field_map(self) -> dict[str, ImportFieldRule]:
        """Маппинг canonical_name → правило поля."""
        return {field.canonical_name: field for field in self.fields}

    @cached_property
    def derived_map(self) -> dict[str, DerivedFieldRule]:
        """Маппинг target → правило derived-поля."""
        return {rule.target: rule for rule in self.derived_fields}

    @cached_property
    def identity_field(self) -> str | None:
        """Имя поля-идентификатора (например booking_ref)."""
        for field in self.fields:
            if field.is_identity:
                return field.canonical_name
        return None


DEFAULT_BOOKING_IMPORT_SCHEMA = BookingImportSchema(
    fields=(
        # --- identity ---
        ImportFieldRule(
            canonical_name="booking_ref",
            aliases=("booking_ref", "booking_reference", "reservation_id"),
            strip=True,
            is_identity=True,
            nullable=False,
        ),

        # --- даты ---
        ImportFieldRule(
            canonical_name="arrival_date",
            aliases=("arrival_date", "checkin_date", "arrival"),
            semantic="date",
        ),
        ImportFieldRule(
            canonical_name="arrival_date_year",
            aliases=("arrival_date_year", "checkin_year"),
            kind="date_part",
        ),
        ImportFieldRule(
            canonical_name="arrival_date_month",
            aliases=("arrival_date_month", "checkin_month"),
            kind="date_part",
        ),
        ImportFieldRule(
            canonical_name="arrival_date_day_of_month",
            aliases=("arrival_date_day_of_month", "checkin_day"),
            kind="date_part",
        ),
        ImportFieldRule(
            canonical_name="source_updated_at",
            aliases=("source_updated_at", "updated_at", "last_modified"),
            strip=True,
            semantic="datetime",
        ),

        # --- флаги ---
        ImportFieldRule(
            canonical_name="is_cancellation",
            aliases=("is_cancellation", "is_canceled", "cancelled"),
            kind="bool_like",
            nullable=False,
        ),
        ImportFieldRule(
            canonical_name="has_deposit",
            aliases=("has_deposit", "deposit", "deposit_flag"),
            strip=True,
            nullable=False,
        ),

        # --- строковые ---
        ImportFieldRule(
            canonical_name="reserved_room_type",
            aliases=("reserved_room_type", "room_type", "reserved_room"),
            strip=True,
            nullable=False,
        ),
        ImportFieldRule(
            canonical_name="market_segment",
            aliases=("market_segment", "segment"),
            default="Undefined",
            strip=True,
        ),
        ImportFieldRule(
            canonical_name="distribution_channel",
            aliases=("distribution_channel", "channel"),
            default="Undefined",
            strip=True,
        ),

        # --- гости ---
        ImportFieldRule("adults", aliases=("adults",), default=0, kind="int"),
        ImportFieldRule("children", aliases=("children", "kids"), default=0, kind="int"),
        ImportFieldRule("babies", aliases=("babies", "infants"), default=0, kind="int"),
        ImportFieldRule("total_guests", default=0, kind="int"),

        # --- ночи ---
        ImportFieldRule("stays_in_weekend_nights", aliases=("stays_in_weekend_nights", "weekend_nights"), default=0,
                        kind="int"),
        ImportFieldRule("stays_in_week_nights", aliases=("stays_in_week_nights", "week_nights"), default=0, kind="int"),
        ImportFieldRule("total_nights", default=0, kind="int"),

        # --- метрики ---
        ImportFieldRule("lead_time", aliases=("lead_time",), default=0, kind="int"),
        ImportFieldRule("booking_changes", aliases=("booking_changes",), default=0, kind="int"),
        ImportFieldRule("adr", aliases=("adr", "average_daily_rate"), default=0.0, kind="float"),
    ),

    required_input_fields=(
        "is_cancellation",
        "has_deposit",
        "reserved_room_type",
    ),

    required_output_fields=(
        "booking_ref",
        "arrival_date",
    ),

    derived_fields=(
        DerivedFieldRule(
            target="arrival_date",
            sources_any_of=(
                ("arrival_date",),
                ("arrival_date_year", "arrival_date_month", "arrival_date_day_of_month"),
            ),
            conflict_policy="first_valid",
        ),
    ),

    aggregates=(
        AggregateRule(
            target="total_guests",
            sources=("adults", "children", "babies"),
            policy="recompute",
        ),
        AggregateRule(
            target="total_nights",
            sources=("stays_in_weekend_nights", "stays_in_week_nights"),
            policy="recompute",
        ),
    ),

    hash_fields=(
        "arrival_date",
        "lead_time",
        "adr",
        "total_guests",
        "total_nights",
        "booking_changes",
        "has_deposit",
        "is_cancellation",
        "market_segment",
        "distribution_channel",
        "reserved_room_type",
    ),
)
