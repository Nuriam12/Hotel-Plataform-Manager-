from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.models.room import Room
from app.models.stay import Stay
from app.models.client import Client


class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, room: Room) -> Room:
        self.db.add(room)
        await self.db.flush()
        return room

    async def list_by_hotel(self, hotel_id: int) -> list[Room]:
        result = await self.db.execute(
            select(Room)
            .where(Room.hotel_id == hotel_id)
            .order_by(Room.room_number)
        )
        return list(result.scalars().all())

    async def get_by_id_and_hotel(self, hotel_id: int, room_id: int) -> Room | None:
        result = await self.db.execute(
            select(Room).where(Room.hotel_id == hotel_id, Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_by_room_number(self, hotel_id: int, room_number: str) -> Room | None:
        result = await self.db.execute(
            select(Room).where(
                Room.hotel_id == hotel_id, Room.room_number == room_number
            )
        )
        return result.scalar_one_or_none()

    async def get_board(
        self, hotel_id: int
    ) -> list[tuple[Room, Stay | None, Client | None]]:
        """
        Devuelve todas las habitaciones del hotel con su stay activa (si existe)
        y el cliente asociado. Usa outerjoin para que las habitaciones libres
        también aparezcan en el resultado (con stay=None, client=None).
        """
        active_stay = aliased(Stay)
        active_client = aliased(Client)

        stmt = (
            select(Room, active_stay, active_client)
            .outerjoin(
                active_stay,
                (active_stay.room_id == Room.id)
                & (active_stay.hotel_id == hotel_id)
                & (active_stay.status == "active")
                & (active_stay.checkout_datetime.is_(None)),
            )
            .outerjoin(
                active_client,
                active_client.id == active_stay.client_id,
            )
            .where(Room.hotel_id == hotel_id)
            .order_by(Room.room_number)
        )

        result = await self.db.execute(stmt)
        return list(result.tuples().all())