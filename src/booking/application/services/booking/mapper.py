from booking.application.dto.booking.parse import ParsedBookingRow
from booking.infrastructure.db.models import Booking
from shared.errors import MappingError


class BookingOrmMapper:
    """Маппит ParsedBookingRow в ORM-модель Booking."""

    def to_new_entity(
            self,
            row: ParsedBookingRow,
            *,
            hotel_id: int,
    ) -> Booking:
        """Создаёт новую ORM-сущность Booking из распарсенной строки."""
        booking_ref = self._require_booking_ref(row)
        payload_hash = self._require_payload_hash(row)

        booking = Booking(
            hotel_id=hotel_id,
            booking_ref=booking_ref,
            payload_hash=payload_hash,
        )
        self._apply_row_data(booking, row)
        return booking

    def apply_updates(
            self,
            booking: Booking,
            row: ParsedBookingRow,
    ) -> None:
        """Применяет данные строки к существующей ORM-сущности Booking."""
        payload_hash = self._require_payload_hash(row)

        booking.payload_hash = payload_hash
        self._apply_row_data(booking, row)

    @staticmethod
    def _apply_row_data(
            booking: Booking,
            row: ParsedBookingRow,
    ) -> None:
        """
        Применяет к ORM-сущности набор импортируемых полей.
        Общий для create/update.
        """
        booking.arrival_date = row.arrival_date
        booking.lead_time = row.lead_time
        booking.adr = row.adr
        booking.total_guests = row.total_guests
        booking.total_nights = row.total_nights
        booking.booking_changes = row.booking_changes
        booking.has_deposit = row.has_deposit
        booking.is_cancellation = row.is_cancellation
        booking.market_segment = row.market_segment
        booking.distribution_channel = row.distribution_channel
        booking.reserved_room_type = row.reserved_room_type
        booking.day_of_week = row.arrival_date.weekday()
        booking.source_updated_at = row.source_updated_at

    @staticmethod
    def _require_booking_ref(row: ParsedBookingRow) -> str:
        """Проверяет, что booking_ref заполнен."""
        if row.booking_ref is None or not row.booking_ref.strip():
            raise MappingError(
                f"Нельзя маппить строку #{row.row_number}: booking_ref пустой."
            )
        return row.booking_ref

    @staticmethod
    def _require_payload_hash(row: ParsedBookingRow) -> str:
        """Проверяет, что payload_hash заполнен."""
        if row.payload_hash is None or not row.payload_hash.strip():
            raise MappingError(
                f"Нельзя маппить строку #{row.row_number}: payload_hash не заполнен."
            )
        return row.payload_hash
