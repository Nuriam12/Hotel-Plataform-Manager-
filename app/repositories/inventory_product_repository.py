from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory_product import InventoryProduct


class InventoryProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: InventoryProduct) -> InventoryProduct:
        self.db.add(product)
        await self.db.flush()
        return product

    async def list_by_hotel(self, hotel_id: int) -> list[InventoryProduct]:
        result = await self.db.execute(select(InventoryProduct)
        .where(InventoryProduct.hotel_id == hotel_id)
        .order_by(InventoryProduct.name, InventoryProduct.id))
        return list(result.scalars().all())

    async def get_by_id_and_hotel(self, hotel_id: int, product_id: int) -> InventoryProduct | None:
        result = await self.db.execute(
        select(InventoryProduct)
        .where(InventoryProduct.hotel_id == hotel_id, InventoryProduct.id == product_id))
        return result.scalar_one_or_none()