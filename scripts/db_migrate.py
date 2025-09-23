"""
Скрипт для миграции БД: добавляет колонку booking_ref и заполняет её.

Используется вручную при изменении схемы.
"""

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from shared.models import Booking
from shared.db import get_session_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """
    Добавляет колонку booking_ref в таблицу booking и назначает значения по порядку.
    """
    session: Session = get_session_sync()

    try:
        session.execute(text("ALTER TABLE booking ADD COLUMN booking_ref VARCHAR"))
        session.commit()
        logger.info("Колонка booking_ref добавлена")
    except Exception as e:
        session.rollback()
        logger.warning(f"Колонка booking_ref уже существует или возникла ошибка: {e}")

    hotel_ids = session.query(Booking.hotel_id).distinct().all()
    for (hotel_id,) in hotel_ids:
        bookings = (
            session.query(Booking)
            .filter(Booking.hotel_id == hotel_id)
            .order_by(Booking.id)
            .all()
        )
        for idx, booking in enumerate(bookings, start=1):
            booking.booking_ref = str(idx)

    session.commit()
    logger.info("Значения booking_ref присвоены")


if __name__ == "__main__":
    migrate()
