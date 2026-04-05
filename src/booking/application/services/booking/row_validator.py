from booking.application.domain.validation.base import BookingRowRule
from booking.application.dto.booking.parse import ParsedBookingRow
from booking.application.dto.booking.validation import BookingValidationResult, RowValidationError
from shared.errors import BusinessValidationError


class BookingRowValidator:
    """Прогоняет строки бронирований через набор бизнес-правил."""

    def __init__(self, rules: list[BookingRowRule]) -> None:
        self._rules = rules

    def validate_many(
            self,
            rows: list[ParsedBookingRow],
    ) -> BookingValidationResult:
        """
        Валидирует список строк.

        Валидные строки собираются в valid_rows,
        ошибки бизнес-валидации — в errors.
        """
        result = BookingValidationResult()

        for row in rows:
            try:
                self.validate_row(row)
                result.valid_rows.append(row)
            except BusinessValidationError as exc:
                result.errors.append(
                    RowValidationError(
                        row_number=row.row_number,
                        message=str(exc),
                    )
                )

        return result

    def validate_row(self, row: ParsedBookingRow) -> None:
        """Прогоняет одну строку через все бизнес-правила."""
        for rule in self._rules:
            rule.check(row)
