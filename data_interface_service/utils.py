from io import StringIO
from datetime import date
import pandas as pd
from sqlalchemy.orm import Session
from shared.models import Booking
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

month_map = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}


def make_date(row):
    """
    Формирует дату заезда из строки arrival_date или из частей (год, месяц, день).
    """
    if "arrival_date" in row and pd.notna(row["arrival_date"]):
        try:
            return pd.to_datetime(row["arrival_date"], format="%d.%m.%Y").date()
        except Exception as e:
            logger.error("Ошибка разбора arrival_date: %s", e)
            raise HTTPException(status_code=400, detail="Неверный формат даты в 'arrival_date'. Ожидается DD.MM.YYYY")

    try:
        return date(
            int(row['arrival_date_year']),
            month_map[row['arrival_date_month']],
            int(row['arrival_date_day_of_month'])
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Невозможно разобрать дату: проверьте arrival_date_year/month/day_of_month")


def detect_separator(content: str) -> str:
    """
    Определяет разделитель CSV на основе первых строк.
    """
    sample = content[:1000]
    return ';' if sample.count(';') > sample.count(',') else ','


def parse_booking_csv(content: str, hotel_id: int, db: Session):
    """
    Парсинг CSV с бронированиями:
    - проверка обязательных колонок,
    - формирование Booking объектов,
    - отбрасывание дубликатов.
    """
    if not content.strip():
        raise HTTPException(status_code=400, detail="Загруженный файл пуст.")

    try:
        sep = detect_separator(content)
        df = pd.read_csv(StringIO(content), sep=sep)
    except Exception as e:
        logger.error("Ошибка чтения CSV: %s", e)
        raise HTTPException(status_code=400, detail="Ошибка при чтении CSV: неверный формат или разделитель.")

    if df.empty:
        raise HTTPException(status_code=400, detail="Файл не содержит данных.")

    # Проверка обязательных колонок
    if not (
        "arrival_date" in df.columns or
        all(c in df.columns for c in ["arrival_date_year", "arrival_date_month", "arrival_date_day_of_month"])
    ):
        raise HTTPException(status_code=400, detail="Отсутствует дата прибытия: используйте 'arrival_date' или три колонки с годом, месяцем и днём.")

    required_columns = ["is_cancellation", "has_deposit", "reserved_room_type"]
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Отсутствует обязательная колонка: {col}")

    # Заполнение необязательных полей
    df['market_segment'] = df.get('market_segment', 'Undefined')
    df['distribution_channel'] = df.get('distribution_channel', 'Undefined')
    df["booking_ref"] = df.get("booking_ref", pd.Series(dtype=str)).fillna("")

    for col in ["adults", "children", "babies", "total_guests"]:
        df[col] = df.get(col, 0).fillna(0)

    for col in ["stays_in_weekend_nights", "stays_in_week_nights", "total_nights"]:
        df[col] = df.get(col, 0).fillna(0)

    for col in ["lead_time", "booking_changes", "adr"]:
        df[col] = df.get(col, 0).fillna(0)

    # Дубликаты booking_ref
    existing_refs = {
        ref for (ref,) in db.query(Booking.booking_ref)
        .filter(Booking.hotel_id == hotel_id)
        .filter(Booking.booking_ref.isnot(None))
        .all()
    }

    bookings = []
    duplicates_skipped = 0

    for _, row in df.iterrows():
        try:
            # Проверка гостей
            total_guests = int(row.get("total_guests") or (row["adults"] + row["children"] + row["babies"]))
            if total_guests <= 0:
                logger.warning("Пропущена строка: total_guests=0")
                continue

            # Проверка ночей
            total_nights = int(row.get("total_nights") or (row["stays_in_weekend_nights"] + row["stays_in_week_nights"]))
            if total_nights <= 0:
                logger.warning("Пропущена строка: total_nights=0")
                continue

            # Дубликаты
            booking_ref = str(row["booking_ref"]).strip()
            if booking_ref and booking_ref in existing_refs:
                duplicates_skipped += 1
                logger.info("Пропущен дубликат booking_ref=%s", booking_ref)
                continue

            arrival = make_date(row)
            is_cancel = bool(row["is_cancellation"])
            has_deposit = str(row["has_deposit"]).lower() != "no deposit"

            booking = Booking(
                hotel_id=hotel_id,
                booking_ref=booking_ref if booking_ref else None,
                arrival_date=arrival,
                lead_time=int(row["lead_time"]),
                adr=float(row["adr"]),
                total_guests=total_guests,
                total_nights=total_nights,
                booking_changes=int(row["booking_changes"]),
                has_deposit=has_deposit,
                is_cancellation=is_cancel,
                market_segment=row["market_segment"],
                distribution_channel=row["distribution_channel"],
                reserved_room_type=row["reserved_room_type"],
                day_of_week=arrival.weekday()
            )
            bookings.append(booking)

        except Exception as e:
            logger.error("Ошибка в строке CSV: %s", e)
            raise HTTPException(status_code=400, detail="Ошибка в одной из строк CSV. Проверьте данные.")

    if not bookings and duplicates_skipped == 0:
        raise HTTPException(status_code=400, detail="Не удалось добавить ни одной записи. Проверьте содержимое файла.")

    logger.info("Добавлено %s записей, пропущено %s дубликатов.", len(bookings), duplicates_skipped)
    return bookings, duplicates_skipped
