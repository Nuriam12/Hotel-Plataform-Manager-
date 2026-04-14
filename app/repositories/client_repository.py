from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client


class ClientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, client: Client) -> Client:
        self.db.add(client)
        await self.db.flush()
        return client

    async def list_by_hotel(self, hotel_id: int) -> list[Client]:
        result = await self.db.execute(
            select(Client)
            .where(Client.hotel_id == hotel_id)
            .order_by(Client.name, Client.id)
        )
        return list(result.scalars().all())

    async def get_by_id_and_hotel(
        self, hotel_id: int, client_id: int
    ) -> Client | None:
        result = await self.db.execute(
            select(Client).where(
                Client.hotel_id == hotel_id,
                Client.id == client_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_dni(self, hotel_id: int, dni: str) -> Client | None:
        result = await self.db.execute(
            select(Client).where(
                Client.hotel_id == hotel_id,
                Client.dni == dni,
            )
        )
        return result.scalar_one_or_none()