import logging

from fastapi import APIRouter, File, UploadFile, status

from booking.api.dependencies import (
    ImportBookingsUseCaseDep,
    AuthorizedHotelIdDep,
    UoWDep,
)
from booking.api.mappers import (
    map_import_report_to_response,
    map_booking_daily_stats_list_to_response,
    map_booking_daily_stats_query_to_dto,
)
from booking.api.schemas import (
    BookingDailyStatsResponse,
    BookingDailyStatsQuery,
    BookingImportResponse,
)
from booking.application.use_cases.get_booking_daily_stats import get_booking_daily_stats
from shared.errors import (
    register_errors,
    ImportFormatError,
    MappingError,
    BusinessValidationError,
    AuthorizationError,
    DatabaseError
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/import",
    response_model=BookingImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Импорт бронирований из CSV-файла",
    response_description="Возвращает результат импорта бронирований",
)
@register_errors(
    AuthorizationError,
    ImportFormatError,
    MappingError,
    BusinessValidationError,
    DatabaseError,
)
async def import_bookings(
        use_case: ImportBookingsUseCaseDep,
        hotel_id: AuthorizedHotelIdDep,
        file: UploadFile = File(...),
) -> BookingImportResponse:
    logger.info(
        "Получен файл бронирований от hotel_id=%s: %s",
        hotel_id,
        file.filename,
    )

    report = await use_case.execute(
        hotel_id=hotel_id,
        file=file,
    )
    logger.info(
        "Импорт завершён: hotel_id=%s, добавлено=%s, обновлено=%s, без_изменений=%s, отклонено=%s",
        hotel_id,
        report.inserted,
        report.updated,
        report.unchanged,
        report.rejected,
    )

    return map_import_report_to_response(hotel_id=hotel_id, report=report)


@router.get(
    "/daily-stats",
    response_model=list[BookingDailyStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить агрегированную статистику бронирований по дням",
)
@register_errors(AuthorizationError, DatabaseError)
async def get_daily_booking_stats(
        uow: UoWDep,
        hotel_id: AuthorizedHotelIdDep,
        api_query: BookingDailyStatsQuery,
) -> list[BookingDailyStatsResponse]:
    logger.debug(
        "Запрос статистики бронирований: hotel_id=%s, date_from=%s, date_to=%s, has_deposit=%s",
        hotel_id,
        api_query.date_from,
        api_query.date_to,
        api_query.has_deposit,
    )
    query = map_booking_daily_stats_query_to_dto(
        hotel_id=hotel_id,
        query=api_query,
    )

    items = await get_booking_daily_stats(
        uow=uow,
        query=query,
    )

    logger.debug(
        "Статистика получена: hotel_id=%s, количество_дней=%s",
        hotel_id,
        len(items),
    )

    return map_booking_daily_stats_list_to_response(items)
