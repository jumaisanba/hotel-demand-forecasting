from abc import ABC, abstractmethod

from booking.application.dto.booking.parse import ParsedBookingRow


class BookingRowRule(ABC):
    """Интерфейс бизнес-правила для строки бронирования."""

    @abstractmethod
    def check(self, row: ParsedBookingRow) -> None:
        """
        Проверяет строку.

        Должен выбрасывать исключение, если правило нарушено.
        """
        pass