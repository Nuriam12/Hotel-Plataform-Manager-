from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError 

from app.repositories.inventory_product_repository import InventoryProductRepository
from app.repositories.inventory_movement_repository import InventoryMovementRepository
from app.models.inventory_product import InventoryProduct
from app.models.inventory_movement import InventoryMovement, MovementType
from app.schemas.inventory import InventoryProductCreate, InventoryProductUpdate, InventoryMovementCreate


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repository = InventoryProductRepository(db)
        self.movement_repository = InventoryMovementRepository(db)

    async def create_product(self, hotel_id: int, data: InventoryProductCreate) -> InventoryProduct:
        product = InventoryProduct(
            hotel_id=hotel_id,
            name=data.name,
            category=data.category,
            price=data.price,
            current_stock=0, 
        )
        try:
            created = await self.product_repository.create(product)
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("No se pudo crear el producto (datos inconsistentes o restricción en base de datos).") from None
        
    async def list_products(self, hotel_id: int) -> list[InventoryProduct]:
        return await self.product_repository.list_by_hotel(hotel_id)

    async def get_product_by_id(self, hotel_id: int, product_id: int) -> InventoryProduct | None:
        return await self.product_repository.get_by_id_and_hotel(hotel_id, product_id)

    async def update_product(
        self, hotel_id: int, product_id: int, data: InventoryProductUpdate
    ) -> InventoryProduct:
        product = await self.product_repository.get_by_id_and_hotel(hotel_id, product_id)
        if product is None:
            raise LookupError("Producto no encontrado.")

        if data.name is not None:
            product.name = data.name
        if data.category is not None:
            product.category = data.category
        if data.price is not None:
            product.price = data.price

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def register_movement(self, hotel_id: int,user_id: int, data: InventoryMovementCreate) -> InventoryMovement:
        product = await self.product_repository.get_by_id_and_hotel(hotel_id, data.product_id)
        if product is None:
            raise LookupError("El producto no existe en este hotel.")
        if data.kind == "out":
            if product.current_stock < data.quantity:
                raise ValueError("No hay suficiente stock para registrar el movimiento.")
            product.current_stock -= data.quantity
        else:
            product.current_stock += data.quantity

        movement_type = MovementType.OUT if data.kind == "out" else MovementType.IN

        movement = InventoryMovement(
            hotel_id=hotel_id,
            product_id=data.product_id,
            created_by=user_id,
            type=movement_type,
            quantity=data.quantity,
            notes=data.notes,
        )
        try:
            created = await self.movement_repository.create(movement)
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("No se pudo registrar el movimiento (datos inconsistentes o restricción en base de datos).") from None
