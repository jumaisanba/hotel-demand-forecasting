# shared/models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from shared.db import Base


class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    region = Column(String)

    hotels = relationship("Hotel", back_populates="city")
    weather = relationship("Weather", back_populates="city")


class Hotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)

    name = Column(String, nullable=False)
    is_city_hotel = Column(Boolean, nullable=False)
    api_key = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    city = relationship("City", back_populates="hotels")
    bookings = relationship("Booking", back_populates="hotel", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="hotel", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotel.id"), nullable=False)
    booking_ref = Column(String, nullable=True)

    arrival_date = Column(Date, nullable=False)
    lead_time = Column(Integer)
    adr = Column(Numeric)
    total_guests = Column(Integer)
    total_nights = Column(Integer)
    booking_changes = Column(Integer)
    has_deposit = Column(Boolean)
    is_cancellation = Column(Boolean)

    market_segment = Column(String)
    distribution_channel = Column(String)
    reserved_room_type = Column(String)
    day_of_week = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    hotel = relationship("Hotel", back_populates="bookings")


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)

    date = Column(Date, nullable=False)
    temp_avg = Column(Numeric)       # среднесуточная температура
    precipitation = Column(Numeric)
    wind_speed = Column(Numeric)
    weather_desc = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    city = relationship("City", back_populates="weather")


class Holiday(Base):
    __tablename__ = "holiday"

    id = Column(Integer, primary_key=True)

    date = Column(Date, nullable=False, unique=True)
    holiday_name = Column(String, nullable=False)
    is_national = Column(Boolean, default=True)
    region = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotel.id"), nullable=False)

    target_date = Column(Date, nullable=False)
    has_deposit = Column(Boolean)

    bookings = Column(Numeric)
    cancellations = Column(Numeric)

    created_at = Column(DateTime, default=datetime.utcnow)

    hotel = relationship("Hotel", back_populates="predictions")
