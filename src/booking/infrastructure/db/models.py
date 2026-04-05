from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Numeric, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import IdMixin, Base


class City(IdMixin, Base):
    __tablename__ = "city"
    __table_args__ = {"schema": "booking"}

    name: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    region: Mapped[str | None]

    hotels: Mapped[list["Hotel"]] = relationship(back_populates="city")


class Hotel(IdMixin, Base):
    __tablename__ = "hotel"
    __table_args__ = {"schema": "booking"}

    city_id: Mapped[int] = mapped_column(ForeignKey("booking.city.id"), nullable=False)

    name: Mapped[str] = mapped_column(nullable=False)
    is_city_hotel: Mapped[bool] = mapped_column(nullable=False)
    api_key: Mapped[str] = mapped_column(unique=True, nullable=False)

    city: Mapped["City"] = relationship(back_populates="hotels")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="hotel",
        cascade="all, delete-orphan"
    )


class Booking(IdMixin, Base):
    __tablename__ = "booking"
    __table_args__ = (
        UniqueConstraint("hotel_id", "booking_ref", name="uq_booking_hotel_ref"),
        {"schema": "booking"}
    )

    booking_ref: Mapped[str] = mapped_column(nullable=False)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("booking.hotel.id"),
        nullable=False,
        index=True,
    )

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

    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Хеш важного набора полей (если source_updated_at нет)
    payload_hash: Mapped[str | None] = mapped_column(nullable=True)

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    hotel: Mapped["Hotel"] = relationship(back_populates="bookings")


class OutboxEvent(Base):
    __tablename__ = "outbox_event"
    __table_args__ = {"schema": "booking"}

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    event_type: Mapped[str] = mapped_column(nullable=False, index=True)
    routing_key: Mapped[str] = mapped_column(nullable=False)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(
        nullable=False,
        server_default="pending",
        index=True,
    )
    retry_count: Mapped[int] = mapped_column(nullable=False, server_default='0')
    last_error: Mapped[str | None] = mapped_column(nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
