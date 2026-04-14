from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.room import Room

class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, room: Room) -> Room: #crea una habitacion y la devuelve
        self.db.add(room)
        await self.db.flush()
        return room

    async def list_by_hotel(self, hotel_id: int) -> list[Room]: #lista todas las habitaciones de un hotel y las devuelve
        result = await self.db.execute(select(Room)
        .where(Room.hotel_id == hotel_id)
        .order_by(Room.room_number))
        return list(result.scalars().all())

    
    async def get_by_id_and_hotel(self, hotel_id: int, room_id: int) -> Room | None: #obtiene una habitacion por su id y el hotel
        result = await self.db.execute(select(Room)
        .where(Room.hotel_id == hotel_id, Room.id == room_id))
        return result.scalar_one_or_none()


    async def get_by_room_number(self, hotel_id: int, room_number: str) -> Room | None: #obtiene una habitacion por su numero y el hotel 
        result = await self.db.execute(select(Room)
        .where(Room.hotel_id == hotel_id, Room.room_number == room_number))
        return result.scalar_one_or_none()