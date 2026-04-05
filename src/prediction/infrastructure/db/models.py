from datetime import date, datetime

from sqlalchemy import text, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import IdMixin, Base


class Weather(IdMixin, Base):
    __tablename__ = "weather"
    __table_args__ = {"schema": "forecast"}

    city_id: Mapped[int] = mapped_column(nullable=False)

    day: Mapped[date] = mapped_column(nullable=False)
    temp_avg: Mapped[float | None]  # Среднесуточная температура
    precipitation: Mapped[float | None]
    wind_speed: Mapped[float | None]
    weather_desc: Mapped[str | None]


class Holiday(IdMixin, Base):
    __tablename__ = "holiday"
    __table_args__ = {"schema": "forecast"}

    day: Mapped[date] = mapped_column(nullable=False, unique=True)
    holiday_name: Mapped[str] = mapped_column(nullable=False)
    is_national: Mapped[bool] = mapped_column(default=True, server_default=text("'true'"))
    region: Mapped[str | None]


class Prediction(IdMixin, Base):
    __tablename__ = "prediction"
    __table_args__ = {"schema": "forecast"}

    hotel_id: Mapped[int] = mapped_column(nullable=False)

    target_date: Mapped[date] = mapped_column(nullable=False)
    has_deposit: Mapped[bool | None]

    bookings: Mapped[float | None]
    cancellations: Mapped[float | None]


class BookingProjection(Base):
    """
    Проекция бронирований для prediction-сервиса.

    Локальный read-model, обновляется через события из booking.
    """
    __tablename__ = "booking_projection"
    __table_args__ = (
        UniqueConstraint("hotel_id", "booking_ref", name="uq_projection_hotel_ref"),
        {"schema": "forecast"},
    )
    booking_ref: Mapped[str] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(primary_key=True)

    arrival_date: Mapped[date] = mapped_column(nullable=False)
    lead_time: Mapped[int | None]
    adr: Mapped[float | None]
    total_guests: Mapped[int | None]
    total_nights: Mapped[int | None]

    booking_changes: Mapped[int | None]
    has_deposit: Mapped[bool | None]
    is_cancellation: Mapped[bool | None]

    market_segment: Mapped[str | None]
    distribution_channel: Mapped[str | None]
    reserved_room_type: Mapped[str | None]
    day_of_week: Mapped[int | None]

    source_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    payload_hash: Mapped[str | None]

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )



class HotelProjection(Base):
    """Проекция отеля для prediction-сервиса."""

    __tablename__ = "hotel_projection"
    __table_args__ = {"schema": "forecast"}

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(nullable=False)
    is_city_hotel: Mapped[bool] = mapped_column(nullable=False)