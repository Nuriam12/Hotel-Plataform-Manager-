from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.stay import Stay


class StayRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, stay: Stay) -> Stay: #crea un stay en la base de datos 
        self.db.add(stay)
        await self.db.flush()
        return stay

    async def list_by_hotel(self, hotel_id: int) -> list[Stay]:
        result = await self.db.execute(
            select(Stay)
            .where(Stay.hotel_id == hotel_id)
            .order_by(Stay.checkin_datetime.desc(), Stay.id.desc())
        )
        return list(result.scalars().all())

    async def list_by_hotel_filtered(
        self, hotel_id: int, status: str | None = None
    ) -> list[Stay]:
        query = (
            select(Stay)
            .where(Stay.hotel_id == hotel_id)
            .order_by(Stay.checkin_datetime.desc(), Stay.id.desc())
        )
        if status is not None:
            query = query.where(Stay.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_hotel(self, hotel_id: int, stay_id: int) -> Stay | None:
        result = await self.db.execute(
            select(Stay).where(Stay.hotel_id == hotel_id, Stay.id == stay_id)
        )
        return result.scalar_one_or_none()

    async def has_active_stay_for_room(self, hotel_id: int, room_id: int) -> bool:
        result = await self.db.execute(
            select(Stay.id).where(
                Stay.hotel_id == hotel_id,
                Stay.room_id == room_id,
                Stay.checkout_datetime.is_(None),
                Stay.status == "active",
            )
        )
        return result.first() is not None

    async def get_active_stay_for_room(self, hotel_id: int, room_id: int) -> Stay | None:
        result = await self.db.execute(
            select(Stay).where(
                Stay.hotel_id == hotel_id,
                Stay.room_id == room_id,
                Stay.checkout_datetime.is_(None),
                Stay.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def list_completed_this_month(self, hotel_id: int) -> list[Stay]:
        from datetime import datetime

        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(Stay).where(
                Stay.hotel_id == hotel_id,
                Stay.status == "completed",
                Stay.checkout_datetime >= month_start,
            )
        )
        return list(result.scalars().all())

    async def next_account_number(self, hotel_id: int) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.max(Stay.account_number), 0)).where(
                Stay.hotel_id == hotel_id
            )
        )
        current_max: int = result.scalar_one()
        return current_max + 1