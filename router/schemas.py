from datetime import date
from typing import List
from pydantic import BaseModel


# === AUTH ===
class AuthRequest(BaseModel):
    """Запрос авторизации по API-ключу"""
    api_key: str


# === PREDICTION (генерация прогноза моделью) ===
class PredictionRequest(BaseModel):
    """Запрос на генерацию прогноза с использованием модели"""
    hotel_id: int
    target_date: date
    has_deposit: bool


class PredictionDay(BaseModel):
    """День прогноза (результаты модели)"""
    date: str
    bookings: float
    cancellations: float


class PredictionResponse(BaseModel):
    """Ответ на запрос прогноза модели"""
    hotel_id: int
    target_date: date
    forecast: List[PredictionDay]


# === FORECAST (чтение сохранённых прогнозов из БД через data_interface) ===
class ForecastRequest(BaseModel):
    """Запрос сохранённого прогноза"""
    target_date: str  # YYYY-MM-DD
    horizon: int      # 7 или 30
    has_deposit: bool


class ForecastDay(BaseModel):
    """День сохранённого прогноза (из БД)"""
    date: str
    bookings: float
    cancellations: float


class ForecastResponse(BaseModel):
    """Ответ с сохранённым прогнозом из БД"""
    hotel_id: int
    forecast: List[ForecastDay]
