from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.client_consumption import ClientConsumption
from app.schemas.consumption import ClientConsumptionCreate, ClientConsumptionRead


class ConsumptionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, row: ClientConsumption) -> ClientConsumption:
        self.db.add(row)
        await self.db.flush()
        return row
    
    async def list_by_hotel(self, hotel_id: int) -> list[ClientConsumption]:
        result = await self.db.execute(select(ClientConsumption)
        .where(ClientConsumption.hotel_id == hotel_id)
        .order_by(ClientConsumption.created_at))
        return list(result.scalars().all())

    async def list_by_stay(self, hotel_id: int, stay_id: int) -> list[ClientConsumption]:
        result = await self.db.execute(select(ClientConsumption)
        .where(ClientConsumption.stay_id == stay_id,
        ClientConsumption.hotel_id == hotel_id)
        .order_by(ClientConsumption.created_at))
        return list(result.scalars().all())

    async def get_by_id_and_hotel(self, hotel_id: int, consumption_id: int) -> ClientConsumption | None:
        result = await self.db.execute(select(ClientConsumption)
        .where(ClientConsumption.hotel_id == hotel_id, ClientConsumption.id == consumption_id))
        return result.scalar_one_or_none()
