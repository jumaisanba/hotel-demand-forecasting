import pandas as pd

from prediction.application.ports.repositories import (
    IBookingProjectionRepository,
    IHolidayRepository,
    IHotelProjectionRepository,
    IWeatherRepository,
)
from shared.errors import ValidationError


class ForecastDataLoader:
    """Загружает данные для прогноза через репозитории."""

    def __init__(
            self,
            bookings: IBookingProjectionRepository,
            hotels: IHotelProjectionRepository,
            weather: IWeatherRepository,
            holidays: IHolidayRepository,
    ) -> None:
        self._bookings = bookings
        self._hotels = hotels
        self._weather = weather
        self._holidays = holidays

    async def load_bookings(self, hotel_id: int) -> pd.DataFrame:
        """Загружает данные о бронированиях для указанного отеля."""
        records = await self._bookings.get_by_hotel(hotel_id)
        if not records:
            raise ValidationError(f"Нет данных о бронированиях для hotel_id={hotel_id}")

        df = pd.DataFrame(
            [
                {
                    "booking_ref": b.booking_ref,
                    "hotel_id": b.hotel_id,
                    "arrival_date": b.arrival_date,
                    "lead_time": b.lead_time,
                    "adr": b.adr,
                    "total_guests": b.total_guests,
                    "total_nights": b.total_nights,
                    "booking_changes": b.booking_changes,
                    "has_deposit": b.has_deposit,
                    "is_cancellation": b.is_cancellation,
                    "market_segment": b.market_segment,
                    "distribution_channel": b.distribution_channel,
                    "reserved_room_type": b.reserved_room_type,
                    "day_of_week": b.day_of_week,
                    "source_updated_at": b.source_updated_at,
                    "payload_hash": b.payload_hash,
                    "updated_at": b.updated_at,
                }
                for b in records
            ]
        )
        df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce")
        return df

    async def load_weather(self, hotel_id: int) -> pd.DataFrame:
        """Загружает погодные данные по городу отеля."""
        hotel = await self._hotels.get_by_id(hotel_id)
        if hotel is None:
            raise ValidationError(f"Не найден hotel_id={hotel_id}")

        records = await self._weather.get_by_city(hotel.city_id)
        if not records:
            raise ValidationError(f"Нет погодных данных для city_id={hotel.city_id}")

        df = pd.DataFrame(
            [{"day": w.day, "temp_avg": w.temp_avg} for w in records]
        )
        df["day"] = pd.to_datetime(df["day"], errors="coerce")
        df["temp_avg"] = pd.to_numeric(df["temp_avg"], errors="coerce")
        return df

    async def load_holidays(self) -> pd.DataFrame:
        """Загружает данные о праздничных днях."""
        records = await self._holidays.list_all()
        if not records:
            raise ValidationError("Данные о праздничных днях отсутствуют")

        df = pd.DataFrame(
            [{"day": h.day, "holiday_name": h.holiday_name, "region": h.region} for h in records]
        )
        df["day"] = pd.to_datetime(df["day"], errors="coerce")
        return df

    async def get_hotel_projection(self, hotel_id: int):
        """Возвращает проекцию отеля."""
        hotel = await self._hotels.get_by_id(hotel_id)
        if hotel is None:
            raise ValidationError(f"Не найден hotel_id={hotel_id}")
        return hotel
