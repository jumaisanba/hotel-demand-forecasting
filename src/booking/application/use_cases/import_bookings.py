from uuid import uuid4

from booking.application.dto.booking.import_report import BookingImportReport
from booking.application.dto.booking.parse import ParsedBookingRow
from booking.application.dto.events import BookingUpsertedEvent
from booking.application.dto.outbox import NewOutboxEvent
from booking.application.ports.booking_reader import IBookingReader
from booking.application.ports.unit_of_work import IUnitOfWork
from booking.application.services.booking import (
    BookingChangeDetector,
    BookingDataFramePreprocessor,
    BookingHashBuilder,
    BookingOrmMapper,
    BookingRowParser,
    BookingRowValidator,
)


class ImportBookingsUseCase:
    def __init__(
            self,
            reader: IBookingReader,
            preprocessor: BookingDataFramePreprocessor,
            row_parser: BookingRowParser,
            row_validator: BookingRowValidator,
            hash_builder: BookingHashBuilder,
            change_detector: BookingChangeDetector,
            mapper: BookingOrmMapper,
            uow: IUnitOfWork,
    ) -> None:
        self._reader = reader
        self._preprocessor = preprocessor
        self._row_parser = row_parser
        self._row_validator = row_validator
        self._hash_builder = hash_builder
        self._change_detector = change_detector
        self._mapper = mapper
        self._uow = uow

    async def execute(
            self,
            *,
            hotel_id: int,
            file,
    ) -> BookingImportReport:
        raw_df = await self._reader.read(file)
        total_rows = len(raw_df)

        prepared_df = self._preprocessor.process(raw_df)

        parse_result = self._row_parser.parse_many(prepared_df)

        validation_result = self._row_validator.validate_many(parse_result.parsed_rows)

        hashed_rows = [
            self._build_payload_hash(row)
            for row in validation_result.valid_rows
        ]

        booking_refs = [
            row.booking_ref
            for row in hashed_rows
            if row.booking_ref is not None
        ]

        async with self._uow:
            existing_state = await self._uow.bookings.get_existing_state_by_refs(
                hotel_id=hotel_id,
                booking_refs=booking_refs,
            )

            diff_result = self._change_detector.detect(
                rows=hashed_rows,
                existing_state=existing_state,
            )

            new_entities = [
                self._mapper.to_new_entity(row, hotel_id=hotel_id)
                for row in diff_result.to_insert
            ]
            await self._uow.bookings.add_many(new_entities)

            refs_to_update = [
                row.booking_ref
                for row in diff_result.to_update
                if row.booking_ref is not None
            ]

            existing_entities = await self._uow.bookings.get_by_refs(
                hotel_id=hotel_id,
                booking_refs=refs_to_update,
            )

            for row in diff_result.to_update:
                if row.booking_ref is None:
                    continue

                booking = existing_entities.get(row.booking_ref)
                if booking is None:
                    # Защита от рассинхрона между lightweight state и фактической загрузкой сущностей
                    continue

                self._mapper.apply_updates(booking, row)

            outbox_events = self._build_outbox_events(
                hotel_id=hotel_id,
                rows=[*diff_result.to_insert, *diff_result.to_update],
            )
            for event in outbox_events:
                await self._uow.outbox.add(event)

            await self._uow.commit()

        return BookingImportReport(
            total_rows=total_rows,
            parsed_rows=len(parse_result.parsed_rows),
            parse_errors=len(parse_result.errors),
            valid_rows=len(validation_result.valid_rows),
            validation_errors=len(validation_result.errors),
            inserted=len(diff_result.to_insert),
            updated=len(diff_result.to_update),
            unchanged=len(diff_result.unchanged),
            rejected=len(diff_result.rejected),
        )

    def _build_payload_hash(self, row: ParsedBookingRow) -> ParsedBookingRow:
        payload_hash = self._hash_builder.build_from_parsed_row(row)
        return row.with_payload_hash(payload_hash)

    @staticmethod
    def _build_outbox_events(
            *,
            hotel_id: int,
            rows: list[ParsedBookingRow],
    ) -> list[NewOutboxEvent]:
        """Формирует outbox-события для изменённых бронирований."""
        events: list[NewOutboxEvent] = []

        for row in rows:
            event = BookingUpsertedEvent.create(
                hotel_id=hotel_id,
                row=row,
            )
            events.append(
                NewOutboxEvent(
                    id=event.event_id,
                    event_type=event.event_type,
                    routing_key="booking.upserted",
                    payload=event.to_dict(),
                )
            )

        return events
