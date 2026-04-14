from sqlalchemy import String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.models.base_model import TimestampMixin


class Stay(TimestampMixin, Base):
    __tablename__ = "stays"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    reservation_id: Mapped[int | None] = mapped_column(ForeignKey("reservations.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    checkin_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    checkout_datetime: Mapped[datetime | None] = mapped_column(DateTime)
    price_per_night: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text)