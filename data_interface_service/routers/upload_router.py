from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from shared.db import get_session
from shared.models import Hotel
from data_interface_service.utils import parse_booking_csv
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
def upload_bookings(
    file: UploadFile = File(...),
    x_hotel_id: int = Header(...),
    db: Session = Depends(get_session)
):
    logger.info("Получен файл бронирований от hotel_id=%s: %s", x_hotel_id, file.filename)

    # Проверка отеля
    hotel = db.query(Hotel).filter(Hotel.id == x_hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=401, detail="Неверный идентификатор отеля")

    try:
        content = file.file.read().decode("utf-8")
        if not content.strip():
            raise HTTPException(status_code=400, detail="Загруженный файл пуст")

        bookings, duplicates_skipped = parse_booking_csv(content, hotel.id, db)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("Ошибка обработки файла")
        raise HTTPException(status_code=400, detail="Ошибка обработки CSV")

    if not bookings and duplicates_skipped > 0:
        return JSONResponse(
            status_code=400,
            content={
                "status": "no_new_records",
                "message": "Все записи уже существуют, новые бронирования не добавлены.",
                "added": 0,
                "duplicates_skipped": duplicates_skipped,
            },
        )
    elif not bookings:
        return JSONResponse(
            status_code=400,
            content={
                "status": "no_valid_records",
                "message": "Файл не содержит валидных бронирований.",
                "added": 0,
                "duplicates_skipped": 0,
            },
        )

    try:
        db.add_all(bookings)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Ошибка сохранения данных в БД")
        raise HTTPException(status_code=500, detail="Ошибка сохранения данных в базу")

    return {
        "status": "ok",
        "added": len(bookings),
        "duplicates_skipped": duplicates_skipped,
        "message": "Бронирования успешно загружены.",
    }
