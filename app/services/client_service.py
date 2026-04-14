from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate
from app.models.client import Client

class ClientService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.client_repository = ClientRepository(db)

    async def create (self, hotel_id: int, data: ClientCreate) -> Client:
        client = Client(
            hotel_id=hotel_id,
            dni=data.dni,
            name=data.name,
            phone=data.phone,
        )
        try:
            created = await self.client_repository.create(client)
            await self.db.commit()
            await self.db.refresh(created)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Error al crear el cliente: {str(e)}")
        return created

    async def list_clients(self, hotel_id: int) -> list[Client]:
        return await self.client_repository.list_by_hotel(hotel_id)

    async def get_client_by_id(self, hotel_id: int, client_id: int) -> Client | None:
        return await self.client_repository.get_by_id_and_hotel(hotel_id, client_id)