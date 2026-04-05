from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ForecastSeriesDay(BaseModel):
    """Точка временного ряда прогноза или истории."""

    day: date = Field(..., description="Дата")
    bookings: float = Field(..., ge=0, description="Количество бронирований")
    cancellations: float = Field(..., ge=0, description="Количество отмен")

    model_config = ConfigDict(from_attributes=True)


class ForecastRequest(BaseModel):
    """Запрос на получение истории и прогноза бронирований."""

    target_date: date = Field(..., description="Целевая дата прогноза")
    horizon: int = Field(..., ge=0, le=30, description="Горизонт прогноза, дней")
    history_window: int = Field(30, ge=1, le=90, description="Окно истории, дней")
    has_deposit: bool = Field(..., description="True — с депозитом, False — без")


class ForecastResponse(BaseModel):
    """Ответ с историей и прогнозом."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    history_summary: list[ForecastSeriesDay] = Field(..., description="История бронирований")
    forecast: list[ForecastSeriesDay] = Field(..., description="Прогноз бронирований")


class TrainRequest(BaseModel):
    """Запрос на обучение модели."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    epochs: int = Field(10, ge=1, description="Количество эпох обучения")
    batch_size: int = Field(32, ge=1, description="Размер батча")
    init: bool = Field(False, description="Инициализировать модель из базового шаблона")


class TrainResponse(BaseModel):
    """Ответ на запуск обучения."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    message: str = Field(..., description="Результат запуска обучения")


class InitHotelResponse(BaseModel):
    """Ответ на инициализацию модели отеля."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    path: str = Field(..., description="Путь к директории модели")


class ModelStatusResponse(BaseModel):
    """Статус наличия модели и конфигурации."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    model_exists: bool = Field(..., description="Флаг наличия файла модели")
    config_exists: bool = Field(..., description="Флаг наличия конфигурации модели")


class ModelConfigResponse(BaseModel):
    """Конфигурация модели отеля."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    config: dict[str, Any] = Field(..., description="Конфигурация модели")


class PredictRequest(BaseModel):
    """Запрос на запуск прогноза."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    target_date: date = Field(..., description="Дата начала прогноза")
    has_deposit: bool = Field(..., description="Фильтр по наличию депозита")


class PredictResponse(BaseModel):
    """Ответ с результатом прогноза."""

    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    target_date: date = Field(..., description="Дата начала прогноза")
    forecast: list[ForecastSeriesDay] = Field(..., description="Прогноз по дням")