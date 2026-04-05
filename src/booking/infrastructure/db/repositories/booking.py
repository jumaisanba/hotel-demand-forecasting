from datetime import date

from sqlalchemy import select, func, case

from booking.application.dto.booking.diff import ExistingBookingState
from booking.application.dto.booking.history import BookingDailyStats
from booking.application.ports.repositories import IBookingRepository
from booking.infrastructure.db.models import Booking


class BookingRepository(IBookingRepository):
    """Репозиторий для работы с бронированиями."""

    def __init__(self, session):
        self._session = session

    async def get_existing_state_by_refs(
            self,
            hotel_id: int,
            booking_refs: list[str],
    ) -> dict[str, ExistingBookingState]:
        """
        Возвращает текущее состояние бронирований по booking_ref.

        Используется при импорте для сравнения входных строк
        с уже существующими записями в БД.
        """
        if not booking_refs:
            return {}

        stmt = (
            select(
                Booking.booking_ref,
                Booking.payload_hash,
                Booking.source_updated_at,
            )
            .where(Booking.hotel_id == hotel_id)
            .where(Booking.booking_ref.in_(booking_refs))
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return {
            row.booking_ref: ExistingBookingState(
                booking_ref=row.booking_ref,
                payload_hash=row.payload_hash,
                source_updated_at=row.source_updated_at,
            )
            for row in rows
        }

    async def get_by_refs(
            self,
            hotel_id: int,
            booking_refs: list[str],
    ) -> dict[str, Booking]:
        """Возвращает ORM-модели бронирований по booking_ref."""
        if not booking_refs:
            return {}

        stmt = (
            select(Booking)
            .where(Booking.hotel_id == hotel_id)
            .where(Booking.booking_ref.in_(booking_refs))
        )

        result = await self._session.execute(stmt)
        bookings = result.scalars().all()

        return {
            booking.booking_ref: booking
            for booking in bookings
        }

    async def add(self, booking: Booking) -> None:
        """Добавляет одно бронирование в сессию."""
        self._session.add(booking)

    async def add_many(self, bookings: list[Booking]) -> None:
        """Добавляет несколько бронирований в сессию."""
        if not bookings:
            return

        self._session.add_all(bookings)

    async def get_daily_stats(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool | None = None,
    ) -> list[BookingDailyStats]:
        """Возвращает агрегированную статистику бронирований по дням."""
        bookings_sum = func.count(Booking.id)
        cancellations_sum = func.sum(
            case((Booking.is_cancellation.is_(True), 1), else_=0)
        )

        stmt = (
            select(
                Booking.arrival_date.label("arrival_date"),
                bookings_sum.label("bookings"),
                cancellations_sum.label("cancellations"),
            )
            .where(Booking.hotel_id == hotel_id)
            .where(Booking.arrival_date >= date_from)
            .where(Booking.arrival_date <= date_to)
        )

        if has_deposit is not None:
            stmt = stmt.where(Booking.has_deposit == has_deposit)

        stmt = (
            stmt.group_by(Booking.arrival_date)
            .order_by(Booking.arrival_date.asc())
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            BookingDailyStats(
                arrival_date=row.arrival_date,
                bookings=row.bookings or 0,
                cancellations=row.cancellations or 0,
            )
            for row in rows
        ]
