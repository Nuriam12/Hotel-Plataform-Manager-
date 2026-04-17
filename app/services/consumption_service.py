from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_consumption import ClientConsumption
from app.models.inventory_movement import InventoryMovement, MovementType
from app.repositories.consumption_repository import ConsumptionRepository
from app.repositories.inventory_movement_repository import InventoryMovementRepository
from app.repositories.inventory_product_repository import InventoryProductRepository
from app.repositories.stay_repository import StayRepository
from app.schemas.consumption import ClientConsumptionCreate


class ConsumptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.stay_repository = StayRepository(db)
        self.product_repository = InventoryProductRepository(db)
        self.movement_repository = InventoryMovementRepository(db)
        self.consumption_repository = ConsumptionRepository(db)

    async def record_consumption(
        self,
        hotel_id: int,
        user_id: int,
        data: ClientConsumptionCreate,
    ) -> ClientConsumption:
        stay = await self.stay_repository.get_by_id_and_hotel(
            hotel_id, data.stay_id
        )
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")
        if stay.checkout_datetime is not None or stay.status != "active":
            raise ValueError(
                "Solo se pueden registrar consumos en estancias activas (sin check-out)."
            )

        product = await self.product_repository.get_by_id_and_hotel(
            hotel_id, data.product_id
        )
        if product is None:
            raise LookupError("El producto no existe en este hotel.")

        if product.current_stock < data.quantity:
            raise ValueError("Stock insuficiente para registrar el consumo.")

        unit_price = product.price

        product.current_stock -= data.quantity

        movement_note = f"Consumo estancia id={data.stay_id}"
        if data.notes:
            movement_note = f"{movement_note}. {data.notes}"

        movement = InventoryMovement(
            hotel_id=hotel_id,
            product_id=data.product_id,
            created_by=user_id,
            type=MovementType.OUT,
            quantity=data.quantity,
            notes=movement_note,
        )
        await self.movement_repository.create(movement)

        consumption = ClientConsumption(
            stay_id=data.stay_id,
            hotel_id=hotel_id,
            product_id=data.product_id,
            created_by=user_id,
            quantity=data.quantity,
            unit_price=unit_price,
        )

        try:
            created = await self.consumption_repository.create(consumption)
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                "No se pudo registrar el consumo (restricción en base de datos)."
            ) from None

    async def list_consumptions(
        self, hotel_id: int, stay_id: int | None
    ) -> list[ClientConsumption]:
        if stay_id is not None:
            return await self.consumption_repository.list_by_stay(
                hotel_id, stay_id
            )
        return await self.consumption_repository.list_by_hotel(hotel_id)

    async def cancel_consumption(
        self, hotel_id: int, user_id: int, consumption_id: int
    ) -> ClientConsumption:
        from datetime import datetime, timezone

        consumption = await self.consumption_repository.get_by_id_and_hotel(hotel_id, consumption_id)
        if consumption is None:
            raise LookupError("El consumo no existe en este hotel.")
        if consumption.is_cancelled:
            raise ValueError("El consumo ya está cancelado.")
        
        stay = await self.stay_repository.get_by_id_and_hotel(hotel_id, consumption.stay_id)
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")
        if stay.status == "completed":
            raise ValueError("No se puede cancelar un consumo en una estancia completada.")
        
        product =await self.product_repository.get_by_id_and_hotel(hotel_id, consumption.product_id) 

        if product is None:
            raise LookupError("El producto no existe en este hotel.")
        if product.current_stock < consumption.quantity:
            raise ValueError("No hay suficiente stock para cancelar el consumo.")

        consumption.is_cancelled = True
        consumption.cancelled_at = datetime.now(timezone.utc).replace(tzinfo=None)
        consumption.cancelled_by = user_id

        product.current_stock += consumption.quantity #se restaura el stock del producto

        reverse_movement = InventoryMovement(
        hotel_id=hotel_id,
            product_id=consumption.product_id,
            created_by=user_id,
            type=MovementType.OUT if False else MovementType.IN,
            quantity=consumption.quantity,
            notes=f"Anulación consumo id={consumption_id}, estancia id={consumption.stay_id}",
    )
        await self.movement_repository.create(reverse_movement)
        await self.db.commit()
        await self.db.refresh(consumption)
        return consumption

