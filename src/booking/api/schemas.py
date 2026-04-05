from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingDailyStatsQuery(BaseModel):
    date_from: date = Field(..., description="Начало периода (включительно)")
    date_to: date = Field(..., description="Конец периода (включительно)")
    has_deposit: bool | None = Field(
        default=None,
        description="Фильтр по наличию депозита (True/False) или без фильтра",
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from > self.date_to:
            raise ValueError("date_from must be <= date_to")
        return self


class BookingDailyStatsResponse(BaseModel):
    arrival_date: date = Field(..., description="Дата заезда")
    bookings: float = Field(..., ge=0, description="Количество бронирований")
    cancellations: float = Field(..., ge=0, description="Количество отмен")

    model_config = ConfigDict(from_attributes=True)


class BookingImportResponse(BaseModel):
    hotel_id: int = Field(..., gt=0, description="Идентификатор отеля")
    total_rows: int = Field(..., ge=0, description="Всего строк в файле")
    parsed_rows: int = Field(..., ge=0, description="Успешно распарсенные строки")
    parse_errors: int = Field(..., ge=0, description="Ошибки парсинга")
    valid_rows: int = Field(..., ge=0, description="Валидные строки после проверки")
    validation_errors: int = Field(..., ge=0, description="Ошибки бизнес-валидации")
    inserted: int = Field(..., ge=0, description="Созданные записи")
    updated: int = Field(..., ge=0, description="Обновлённые записи")
    unchanged: int = Field(..., ge=0, description="Без изменений")
    rejected: int = Field(..., ge=0, description="Отклонённые записи")


class HotelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название отеля")
    is_city_hotel: bool = Field(..., description="Флаг городского отеля")


class HotelResponse(BaseModel):
    id: int = Field(..., gt=0, description="Идентификатор отеля")
    name: str = Field(..., min_length=1, max_length=255, description="Название отеля")
    is_city_hotel: bool = Field(..., description="Флаг городского отеля")
    api_key: str = Field(..., min_length=10, description="API-ключ отеля")

    model_config = ConfigDict(from_attributes=True)