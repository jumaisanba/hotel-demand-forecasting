from booking.api.schemas import BookingImportResponse, BookingDailyStatsResponse, BookingDailyStatsQuery, \
    HotelCreateRequest, HotelResponse
from booking.application.dto.booking.history import BookingDailyStats, GetBookingDailyStatsQuery
from booking.application.dto.booking.import_report import BookingImportReport
from booking.application.dto.hotel.create import CreateHotelData, HotelDto


def map_import_report_to_response(
        *,
        hotel_id: int,
        report: BookingImportReport,
) -> BookingImportResponse:
    """Преобразует отчёт импорта в API-ответ."""
    return BookingImportResponse(
        hotel_id=hotel_id,
        total_rows=report.total_rows,
        parsed_rows=report.parsed_rows,
        parse_errors=report.parse_errors,
        valid_rows=report.valid_rows,
        validation_errors=report.validation_errors,
        inserted=report.inserted,
        updated=report.updated,
        unchanged=report.unchanged,
        rejected=report.rejected,
    )


def map_booking_daily_stats_query_to_dto(
        hotel_id: int,
        query: BookingDailyStatsQuery,
) -> GetBookingDailyStatsQuery:
    """Преобразует API-запрос статистики в DTO."""
    return GetBookingDailyStatsQuery(
        hotel_id=hotel_id,
        date_from=query.date_from,
        date_to=query.date_to,
        has_deposit=query.has_deposit,
    )


def map_booking_daily_stats_to_response(
        item: BookingDailyStats,
) -> BookingDailyStatsResponse:
    """Преобразует DTO статистики в API-ответ."""
    return BookingDailyStatsResponse(
        arrival_date=item.arrival_date,
        bookings=item.bookings,
        cancellations=item.cancellations,
    )


def map_booking_daily_stats_list_to_response(
        items: list[BookingDailyStats],
) -> list[BookingDailyStatsResponse]:
    """Преобразует список DTO статистики в API-ответ."""
    return [
        map_booking_daily_stats_to_response(item)
        for item in items
    ]


def map_hotel_create_request_to_dto(
        request: HotelCreateRequest,
) -> CreateHotelData:
    """Преобразует API-запрос создания отеля в DTO."""
    return CreateHotelData(
        name=request.name,
        is_city_hotel=request.is_city_hotel,
    )


def map_hotel_dto_to_response(
        dto: HotelDto,
) -> HotelResponse:
    """Преобразует DTO отеля в API-ответ."""
    return HotelResponse(
        id=dto.id,
        name=dto.name,
        is_city_hotel=dto.is_city_hotel,
        api_key=dto.api_key,
    )
