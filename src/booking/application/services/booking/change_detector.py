from booking.application.dto.booking.diff import BookingDiffResult, ExistingBookingState
from booking.application.dto.booking.diff import BookingRejectReason, RejectedBookingRow
from booking.application.dto.booking.parse import ParsedBookingRow


class BookingChangeDetector:
    """Классифицирует строки: insert / update / unchanged / rejected."""

    def detect(
            self,
            rows: list[ParsedBookingRow],
            existing_state: dict[str, ExistingBookingState],
    ) -> BookingDiffResult:
        """
        Сравнивает импортируемые строки с текущим состоянием в БД.

        Правила:
        - пустой booking_ref -> rejected;
        - дубликат booking_ref внутри батча -> rejected;
        - отсутствует в БД -> to_insert;
        - есть в БД и данные изменились -> to_update;
        - есть в БД и данные не изменились -> unchanged.
        """
        result = BookingDiffResult()
        seen_refs: set[str] = set()

        for row in rows:
            booking_ref = self._normalize_booking_ref(row.booking_ref)

            if not booking_ref:
                result.rejected.append(
                    RejectedBookingRow(
                        row=row,
                        reason=BookingRejectReason.MISSING_BOOKING_REF,
                        message="Строка не содержит booking_ref.",
                    )
                )
                continue

            if booking_ref in seen_refs:
                result.rejected.append(
                    RejectedBookingRow(
                        row=row,
                        reason=BookingRejectReason.DUPLICATE_BOOKING_REF,
                        message=f"Дубликат booking_ref внутри импортируемого батча: {booking_ref}.",
                    )
                )
                continue

            seen_refs.add(booking_ref)

            existing = existing_state.get(booking_ref)
            if existing is None:
                result.to_insert.append(row)
                continue

            if self._should_update(row, existing):
                result.to_update.append(row)
            else:
                result.unchanged.append(row)

        return result

    @staticmethod
    def _normalize_booking_ref(value: str | None) -> str | None:
        """Нормализует booking_ref: убирает пробелы и пустые значения."""
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def _should_update(
            self,
            row: ParsedBookingRow,
            existing: ExistingBookingState,
    ) -> bool:
        """
        Определяет, нужно ли обновлять запись в БД.

        Приоритет:
        - если у обеих сторон есть source_updated_at, сравнение идёт по нему;
        - иначе сравнение идёт по payload_hash.
        """
        if self._can_compare_by_source_updated_at(row, existing):
            return self._is_source_newer(row, existing)

        return self._is_payload_changed(row, existing)

    @staticmethod
    def _can_compare_by_source_updated_at(
            row: ParsedBookingRow,
            existing: ExistingBookingState,
    ) -> bool:
        """Проверяет, что обе стороны содержат source_updated_at для сравнения."""
        return (
                getattr(row, "source_updated_at", None) is not None
                and existing.source_updated_at is not None
        )

    @staticmethod
    def _is_source_newer(
            row: ParsedBookingRow,
            existing: ExistingBookingState,
    ) -> bool:
        """Проверяет, что входная строка новее текущей записи в БД."""
        return row.source_updated_at > existing.source_updated_at

    @staticmethod
    def _is_payload_changed(
            row: ParsedBookingRow,
            existing: ExistingBookingState,
    ) -> bool:
        """Проверяет, изменился ли payload по хешу."""
        return row.payload_hash != existing.payload_hash
