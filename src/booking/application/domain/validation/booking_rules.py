from booking.application.dto.booking.parse import ParsedBookingRow
from booking.application.domain.validation.base import BookingRowRule
from shared.errors import BusinessValidationError


class PositiveGuestsRule(BookingRowRule):
    """Количество гостей должно быть больше 0."""

    def check(self, row: ParsedBookingRow) -> None:
        if row.total_guests <= 0:
            raise BusinessValidationError(
                "Количество гостей должно быть больше 0."
            )


class PositiveNightsRule(BookingRowRule):
    """Количество ночей должно быть больше 0."""

    def check(self, row: ParsedBookingRow) -> None:
        if row.total_nights <= 0:
            raise BusinessValidationError(
                "Количество ночей должно быть больше 0."
            )


class NonNegativeAdrRule(BookingRowRule):
    """ADR не может быть отрицательным."""

    def check(self, row: ParsedBookingRow) -> None:
        if row.adr < 0:
            raise BusinessValidationError(
                "ADR не может быть отрицательным."
            )


class NonEmptyRoomTypeRule(BookingRowRule):
    """Тип комнаты не должен быть пустым."""

    def check(self, row: ParsedBookingRow) -> None:
        if not row.reserved_room_type.strip():
            raise BusinessValidationError(
                "Тип комнаты не должен быть пустым."
            )