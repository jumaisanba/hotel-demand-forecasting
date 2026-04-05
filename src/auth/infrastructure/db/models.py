from datetime import datetime

from sqlalchemy import Enum as SqlEnum, UniqueConstraint, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import IdMixin, Base
from shared.enums import UserRole, SystemRole


class User(IdMixin, Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "auth"}

    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    system_role: Mapped[SystemRole] = mapped_column(
        SqlEnum(SystemRole, name="system_role"),
        nullable=False,
        server_default=SystemRole.user.value,
    )

    hotels: Mapped[list["UserHotel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserHotel(IdMixin, Base):
    __tablename__ = "user_hotel"
    __table_args__ = (
        UniqueConstraint("user_id", "hotel_id", name="uq_user_hotel"),
        {"schema": "auth"},
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth.user.id", ondelete="CASCADE"),
        nullable=False
    )
    hotel_id: Mapped[int] = mapped_column(nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role"),
        nullable=False,
        server_default=UserRole.viewer.value,
    )

    user: Mapped["User"] = relationship(back_populates="hotels")


class ProcessedEvent(Base):
    __tablename__ = "processed_event"
    __table_args__ = {"schema": "auth"}

    event_id: Mapped[str] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column( nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
