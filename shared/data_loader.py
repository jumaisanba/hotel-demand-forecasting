# shared/data_loader.py

import pandas as pd
from sqlalchemy.orm import Session
from shared.models import Booking, Weather, Holiday, Hotel


def load_bookings(hotel_id: int, db: Session) -> pd.DataFrame:
    records = db.query(Booking).filter(Booking.hotel_id == hotel_id).all()
    if not records:
        raise ValueError(f"Нет данных о бронированиях для hotel_id={hotel_id}")
    df = pd.DataFrame([b.__dict__ for b in records])
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    return df


def load_weather(hotel_id: int, db: Session) -> pd.DataFrame:
    # Получение city_id отеля
    city_id = db.query(Hotel.city_id).filter(Hotel.id == hotel_id).scalar()
    if city_id is None:
        raise ValueError(f"Не удалось найти city_id для hotel_id={hotel_id}")

    # Загрузка только нужных столбцов: date и temp_avg
    records = db.query(Weather.date, Weather.temp_avg).filter(Weather.city_id == city_id).all()
    df = pd.DataFrame(records, columns=["date", "temp_avg"])

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        # Убедимся, что temp_avg имеет числовой тип
        df["temp_avg"] = pd.to_numeric(df["temp_avg"], errors="coerce")
    else:
        df["date"] = pd.Series(dtype="datetime64[ns]")
        df["temp_avg"] = pd.Series(dtype="float64")

    return df


def load_holidays(db: Session) -> pd.DataFrame:
    records = db.query(Holiday).all()
    df = pd.DataFrame([h.__dict__ for h in records])
    df['date'] = pd.to_datetime(df['date']) if not df.empty else pd.Series(dtype="datetime64[ns]")
    return df
