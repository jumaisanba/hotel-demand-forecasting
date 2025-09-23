# data_interface_service/routers/prediction_router.py

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from shared.db import get_session_sync
from shared.models import Prediction, Booking
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ForecastRequest(BaseModel):
    target_date: str
    horizon: int
    has_deposit: bool

@router.post("/fetch")
def fetch_forecast(
    req: ForecastRequest,
    x_hotel_id: int = Header(...),
    db: Session = Depends(get_session_sync)
):
    try:
        start_date = datetime.strptime(req.target_date, "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=req.horizon - 1)

        # Исторические данные за последние 30 дней
        history_start = start_date - timedelta(days=29)

        # Группировка по датам
        history_raw = (
            db.query(
                Booking.arrival_date,
                Booking.is_cancellation,
                db.func.count().label("cnt")
            )
            .filter(Booking.hotel_id == x_hotel_id)
            .filter(Booking.arrival_date >= history_start)
            .filter(Booking.arrival_date <= start_date)
            .filter(Booking.has_deposit == req.has_deposit)
            .group_by(Booking.arrival_date, Booking.is_cancellation)
            .all()
        )

        # Переводим в словарь для удобного маппинга
        history_map = {}
        for date_val, is_cancel, cnt in history_raw:
            if date_val not in history_map:
                history_map[date_val] = {"bookings": 0, "cancellations": 0}
            if is_cancel:
                history_map[date_val]["cancellations"] += cnt
            else:
                history_map[date_val]["bookings"] += cnt

        history_data = []
        for offset in range(30):
            day = history_start + timedelta(days=offset)
            history_data.append({
                "date": day.isoformat(),
                "bookings": history_map.get(day, {}).get("bookings", 0),
                "cancellations": history_map.get(day, {}).get("cancellations", 0),
            })

        total_bookings = sum(d["bookings"] for d in history_data)
        if total_bookings < 30:
            return {
                "status": "insufficient_history",
                "message": f"Недостаточно данных для прогноза за {history_start} — {start_date}.",
                "history_summary": history_data,
                "forecast": []
            }

        # Достаём прогноз
        forecast = []
        if req.horizon > 0:
            forecast_records = (
                db.query(Prediction)
                .filter(Prediction.hotel_id == x_hotel_id)
                .filter(Prediction.target_date >= start_date)
                .filter(Prediction.target_date <= end_date)
                .filter(Prediction.has_deposit == req.has_deposit)
                .order_by(Prediction.target_date)
                .all()
            )

            forecast = [
                {
                    "date": record.target_date.isoformat(),
                    "bookings": float(record.bookings),
                    "cancellations": float(record.cancellations),
                }
                for record in forecast_records
            ]

        return {"status": "ok", "history_summary": history_data, "forecast": forecast}

    except Exception as e:
        logger.exception("Ошибка при получении прогноза")
        raise HTTPException(status_code=500, detail="Ошибка при получении прогноза")
