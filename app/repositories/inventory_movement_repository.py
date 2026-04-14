from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_movement import InventoryMovement


class InventoryMovementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, movement: InventoryMovement) -> InventoryMovement:
        self.db.add(movement)
        await self.db.flush()
        return movement
         