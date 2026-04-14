from sqlalchemy import String, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from app.core.database import Base
from app.models.base_model import TimestampMixin

#  La reservacion y la estadia son diferentes. La reservacion es cuando el cliente reserva una habitacion para una fecha determinada.
#  La estadia es cuando el cliente se hospeda en la habitacion.
#  una estadia puede tener o no una reservacion.


class Reservation(TimestampMixin, Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    advance_payment: Mapped[float | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    
    