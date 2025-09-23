from datetime import date
from pydantic import BaseModel
from typing import List

class TrainRequest(BaseModel):
    hotel_id: int
    epochs: int = 10
    batch_size: int = 32
    init: bool = False


class InitHotelRequest(BaseModel):
    hotel_id: int


class PredictRequest(BaseModel):
    hotel_id: int
    target_date: date
    has_deposit: bool


class ForecastDay(BaseModel):
    date: str
    bookings: float
    cancellations: float

    class Config:
        orm_mode = True


class PredictResponse(BaseModel):
    hotel_id: int
    target_date: date
    forecast: List[ForecastDay]