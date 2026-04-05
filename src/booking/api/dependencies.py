import logging
from typing import Annotated

from fastapi import Depends, Header

from booking.application.domain.booking_import import DEFAULT_BOOKING_IMPORT_SCHEMA, BookingImportSchema
from booking.application.domain.validation.base import BookingRowRule
from booking.application.domain.validation.booking_rules import (
    PositiveGuestsRule,
    PositiveNightsRule,
    NonNegativeAdrRule,
    NonEmptyRoomTypeRule,
)
from booking.application.ports.booking_reader import IBookingReader
from booking.application.ports.unit_of_work import IUnitOfWork
from booking.application.services.booking import (
    BookingChangeDetector,
    BookingDataFramePreprocessor,
    BookingDateParser,
    BookingHashBuilder,
    BookingOrmMapper,
    BookingRowParser,
    BookingRowValidator,
)
from booking.application.use_cases.import_bookings import ImportBookingsUseCase
from booking.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from booking.infrastructure.readers.csv_booking_reader import CsvBookingReader
from shared.errors import AuthorizationError

logger = logging.getLogger(__name__)


def get_uow() -> IUnitOfWork:
    """Возвращает Unit of Work для работы с БД."""
    return SQLAlchemyUnitOfWork()


UoWDep = Annotated[IUnitOfWork, Depends(get_uow)]


async def get_authorized_hotel_id(
        uow: UoWDep,
        x_hotel_id: Annotated[int, Header(..., alias="X-Hotel-Id")] = ...,
) -> int:
    """Проверяет существование отеля и возвращает его id."""
    async with uow:
        hotel = await uow.hotels.get_by_id(x_hotel_id)
        if hotel is None:
            logger.warning("Попытка доступа к несуществующему отелю: hotel_id=%s", x_hotel_id)
            raise AuthorizationError()
    return x_hotel_id


AuthorizedHotelIdDep = Annotated[int, Depends(get_authorized_hotel_id)]


def get_current_user_id(
        x_user_id: Annotated[int, Header(..., alias="X-User-Id")],
) -> int:
    """Возвращает id текущего пользователя из доверенного заголовка."""
    if x_user_id <= 0:
        raise AuthorizationError("Некорректный идентификатор пользователя.")
    return x_user_id


CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_booking_import_schema():
    return DEFAULT_BOOKING_IMPORT_SCHEMA


def get_booking_reader() -> IBookingReader:
    return CsvBookingReader()


BookingImportSchemaDep = Annotated[
    BookingImportSchema,
    Depends(get_booking_import_schema),
]
BookingReaderDep = Annotated[IBookingReader, Depends(get_booking_reader)]


def get_booking_df_preprocessor(
        schema: BookingImportSchema = Depends(get_booking_import_schema),
) -> BookingDataFramePreprocessor:
    return BookingDataFramePreprocessor(schema=schema)


def get_booking_date_parser(
        schema: BookingImportSchema = Depends(get_booking_import_schema),
) -> BookingDateParser:
    return BookingDateParser(schema=schema)


def get_booking_row_parser(
        schema: BookingImportSchema = Depends(get_booking_import_schema),
        date_parser: BookingDateParser = Depends(get_booking_date_parser),
) -> BookingRowParser:
    return BookingRowParser(schema=schema, date_parser=date_parser)


def get_booking_validation_rules() -> list[BookingRowRule]:
    return [
        PositiveGuestsRule(),
        PositiveNightsRule(),
        NonNegativeAdrRule(),
        NonEmptyRoomTypeRule(),
    ]


def get_booking_row_validator(
        rules: list[BookingRowRule] = Depends(get_booking_validation_rules),
) -> BookingRowValidator:
    return BookingRowValidator(rules=rules)


def get_booking_hash_builder(
        schema: BookingImportSchema = Depends(get_booking_import_schema),
) -> BookingHashBuilder:
    return BookingHashBuilder(schema=schema)


def get_booking_change_detector() -> BookingChangeDetector:
    return BookingChangeDetector()


def get_booking_orm_mapper() -> BookingOrmMapper:
    return BookingOrmMapper()


BookingDataFramePreprocessorDep = Annotated[
    BookingDataFramePreprocessor,
    Depends(get_booking_df_preprocessor),
]
BookingDateParserDep = Annotated[
    BookingDateParser,
    Depends(get_booking_date_parser),
]
BookingRowParserDep = Annotated[
    BookingRowParser,
    Depends(get_booking_row_parser),
]
BookingRowValidatorDep = Annotated[
    BookingRowValidator,
    Depends(get_booking_row_validator),
]
BookingHashBuilderDep = Annotated[
    BookingHashBuilder,
    Depends(get_booking_hash_builder),
]
BookingChangeDetectorDep = Annotated[
    BookingChangeDetector,
    Depends(get_booking_change_detector),
]
BookingOrmMapperDep = Annotated[
    BookingOrmMapper,
    Depends(get_booking_orm_mapper),
]


def get_import_bookings_use_case(
        reader: BookingReaderDep,
        preprocessor: BookingDataFramePreprocessorDep,
        row_parser: BookingRowParserDep,
        row_validator: BookingRowValidatorDep,
        hash_builder: BookingHashBuilderDep,
        change_detector: BookingChangeDetectorDep,
        mapper: BookingOrmMapperDep,
        uow: UoWDep,
) -> ImportBookingsUseCase:
    """Собирает use-case импорта бронирований."""
    return ImportBookingsUseCase(
        reader=reader,
        preprocessor=preprocessor,
        row_parser=row_parser,
        row_validator=row_validator,
        hash_builder=hash_builder,
        change_detector=change_detector,
        mapper=mapper,
        uow=uow,
    )


ImportBookingsUseCaseDep = Annotated[
    ImportBookingsUseCase,
    Depends(get_import_bookings_use_case),
]
