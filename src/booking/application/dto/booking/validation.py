from dataclasses import dataclass, field

from booking.application.dto.booking.parse import ParsedBookingRow


@dataclass(slots=True, frozen=True)
class RowValidationError:
    """Ошибка бизнес-валидации строки."""

    row_number: int
    message: str


@dataclass(slots=True)
class BookingValidationResult:
    """Результат бизнес-валидации строк бронирований."""

    valid_rows: list[ParsedBookingRow] = field(default_factory=list)
    errors: list[RowValidationError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Есть ли ошибки валидации."""
        return bool(self.errors)
