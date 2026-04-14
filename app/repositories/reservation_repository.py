from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation


class ReservationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, reservation: Reservation) -> Reservation:
        self.db.add(reservation)
        await self.db.flush()
        return reservation

    async def list_by_hotel(self, hotel_id: int) -> list[Reservation]:
        result = await self.db.execute(
            select(Reservation)
            .where(Reservation.hotel_id == hotel_id)
            .order_by(Reservation.start_date.desc(), Reservation.id.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_hotel(
        self, hotel_id: int, reservation_id: int
    ) -> Reservation | None:
        result = await self.db.execute(
            select(Reservation).where(
                Reservation.hotel_id == hotel_id,
                Reservation.id == reservation_id,
            )
        )
        return result.scalar_one_or_none()

    async def has_overlapping_reservation(
        self,
        hotel_id: int,
        room_id: int,
        start_date: date,
        end_date: date,
        exclude_reservation_id: int | None = None,
    ) -> bool:
        conditions = [
            Reservation.hotel_id == hotel_id,
            Reservation.room_id == room_id,
            Reservation.status != "cancelled",
            Reservation.start_date <= end_date,
            Reservation.end_date >= start_date,
        ]
        if exclude_reservation_id is not None:
            conditions.append(Reservation.id != exclude_reservation_id)

        stmt = select(func.count()).select_from(Reservation).where(and_(*conditions))
        total = (await self.db.execute(stmt)).scalar_one()
        return total > 0