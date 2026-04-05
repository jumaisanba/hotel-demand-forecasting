from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BookingImportReport:
    """Сводный отчёт по результатам импорта бронирований."""

    total_rows: int

    parsed_rows: int
    parse_errors: int

    valid_rows: int
    validation_errors: int

    inserted: int
    updated: int
    unchanged: int
    rejected: int
