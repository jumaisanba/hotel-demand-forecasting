from booking.application.dto.booking.history import GetBookingDailyStatsQuery, BookingDailyStats
from booking.application.ports.unit_of_work import IUnitOfWork


async def get_booking_daily_stats(
        uow: IUnitOfWork,
        query: GetBookingDailyStatsQuery,
) -> list[BookingDailyStats]:
    async with uow:
        return await uow.bookings.get_daily_stats(
            hotel_id=query.hotel_id,
            date_from=query.date_from,
            date_to=query.date_to,
            has_deposit=query.has_deposit,
        )
