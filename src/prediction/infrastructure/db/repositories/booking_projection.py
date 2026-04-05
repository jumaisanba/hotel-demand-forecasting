from collections.abc import Sequence
from datetime import date

from sqlalchemy import select, func, case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prediction.application.ports.repositories import IBookingProjectionRepository
from prediction.infrastructure.db.models import BookingProjection


class BookingProjectionRepository(IBookingProjectionRepository):
    """Репозиторий проекции бронирований."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hotel(self, hotel_id: int) -> Sequence[BookingProjection]:
        """Возвращает проекцию бронирований по отелю."""
        stmt = (
            select(BookingProjection)
            .where(BookingProjection.hotel_id == hotel_id)
            .order_by(BookingProjection.arrival_date.asc())
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, booking: BookingProjection) -> None:
        """Создаёт или обновляет запись проекции бронирования."""
        stmt = insert(BookingProjection).values(
            booking_ref=booking.booking_ref,
            hotel_id=booking.hotel_id,
            arrival_date=booking.arrival_date,
            lead_time=booking.lead_time,
            adr=booking.adr,
            total_guests=booking.total_guests,
            total_nights=booking.total_nights,
            booking_changes=booking.booking_changes,
            has_deposit=booking.has_deposit,
            is_cancellation=booking.is_cancellation,
            market_segment=booking.market_segment,
            distribution_channel=booking.distribution_channel,
            reserved_room_type=booking.reserved_room_type,
            day_of_week=booking.day_of_week,
            source_updated_at=booking.source_updated_at,
            payload_hash=booking.payload_hash,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["hotel_id", "booking_ref"],
            set_={
                "arrival_date": stmt.excluded.arrival_date,
                "lead_time": stmt.excluded.lead_time,
                "adr": stmt.excluded.adr,
                "total_guests": stmt.excluded.total_guests,
                "total_nights": stmt.excluded.total_nights,
                "booking_changes": stmt.excluded.booking_changes,
                "has_deposit": stmt.excluded.has_deposit,
                "is_cancellation": stmt.excluded.is_cancellation,
                "market_segment": stmt.excluded.market_segment,
                "distribution_channel": stmt.excluded.distribution_channel,
                "reserved_room_type": stmt.excluded.reserved_room_type,
                "day_of_week": stmt.excluded.day_of_week,
                "source_updated_at": stmt.excluded.source_updated_at,
                "payload_hash": stmt.excluded.payload_hash,
            },
        )

        await self._session.execute(stmt)

    async def get_history_summary(
            self,
            *,
            hotel_id: int,
            date_from: date,
            date_to: date,
            has_deposit: bool,
    ):
        """Возвращает агрегированную историю бронирований по дням."""
        bookings_sum = func.count().label("bookings")
        cancellations_sum = func.sum(
            case((BookingProjection.is_cancellation.is_(True), 1), else_=0)
        ).label("cancellations")

        stmt = (
            select(
                BookingProjection.arrival_date.label("arrival_date"),
                bookings_sum,
                cancellations_sum,
            )
            .where(BookingProjection.hotel_id == hotel_id)
            .where(BookingProjection.arrival_date >= date_from)
            .where(BookingProjection.arrival_date <= date_to)
            .where(BookingProjection.has_deposit == has_deposit)
            .group_by(BookingProjection.arrival_date)
            .order_by(BookingProjection.arrival_date.asc())
        )

        result = await self._session.execute(stmt)
        return result.all()
