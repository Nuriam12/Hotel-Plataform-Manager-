from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate
from app.models.room import Room

class RoomService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.room_repository = RoomRepository(db)

    async def create(self, hotel_id: int,data: RoomCreate) -> Room:
        room = Room(
            hotel_id=hotel_id,
            room_number=data.room_number,
            floor=data.floor,
            room_type=data.room_type,
            price_per_night=data.price_per_night,
            status="available",
        )
        try:
            created = await self.room_repository.create(room)
            await self.db.commit()
            await self.db.refresh(created)
            return created 
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Error al crear la habitacion: {str(e)}")

    async def list_rooms(self, hotel_id: int) -> list[Room]:
        return await self.room_repository.list_by_hotel(hotel_id)

    async def get_room_by_id(self, hotel_id: int, room_id: int) -> Room | None:
        return await self.room_repository.get_by_id_and_hotel(hotel_id, room_id)