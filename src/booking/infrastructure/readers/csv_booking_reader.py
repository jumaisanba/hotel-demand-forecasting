import csv
import logging
from io import StringIO
from typing import BinaryIO

import pandas as pd

from booking.application.ports.booking_reader import IBookingReader
from shared.errors import ImportFormatError

logger = logging.getLogger(__name__)


class CsvBookingReader(IBookingReader):
    """Читает CSV-файл с бронированиями и возвращает DataFrame."""

    def __init__(
            self,
            encoding: str = "utf-8-sig",
            delimiter: str | None = None,
    ) -> None:
        self._encoding = encoding
        self._delimiter = delimiter

    async def read(self, file_obj: BinaryIO) -> pd.DataFrame:
        """
        Читает CSV-файл, определяет разделитель и загружает данные в DataFrame.
        """
        try:
            file_obj.seek(0)
        except (AttributeError, OSError, ValueError):
            pass

        content: bytes = file_obj.read()

        try:
            text = content.decode(self._encoding)
        except UnicodeDecodeError as exc:
            logger.warning("Не удалось декодировать CSV (encoding=%r)", self._encoding)
            raise ImportFormatError("Ошибка декодирования CSV-файла.") from exc

        if not text.strip():
            raise ImportFormatError("Файл пуст.")

        delimiter = self._delimiter or self._detect_separator(text)
        logger.debug("Определён разделитель CSV: %r", delimiter)

        return self._read_csv_to_dataframe(text, delimiter)

    @staticmethod
    def _read_csv_to_dataframe(content: str, delimiter: str) -> pd.DataFrame:
        """Читает CSV-текст в DataFrame с указанным разделителем."""
        try:
            df = pd.read_csv(StringIO(content), sep=delimiter)
        except (pd.errors.ParserError, ValueError) as exc:
            logger.warning(
                "Ошибка парсинга CSV (delimiter=%r): %s",
                delimiter,
                exc,
            )
            raise ImportFormatError(
                "Ошибка чтения CSV (неверный формат или разделитель)."
            ) from exc

        if df.empty:
            raise ImportFormatError("Файл пуст.")

        logger.debug(
            "CSV успешно прочитан: строк=%s, колонок=%s, разделитель=%r",
            df.shape[0],
            df.shape[1],
            delimiter,
        )
        return df

    @staticmethod
    def _detect_separator(content: str) -> str:
        """Определяет разделитель CSV по содержимому файла."""
        sample = content[:2000]
        try:
            return csv.Sniffer().sniff(sample, delimiters=";,").delimiter
        except csv.Error:
            return ";" if sample.count(";") > sample.count(",") else ","
