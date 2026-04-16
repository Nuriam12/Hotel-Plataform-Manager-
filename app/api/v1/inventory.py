from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import AdminUser, StaffUser
from app.schemas.inventory import (
    InventoryMovementCreate,
    InventoryMovementRead,
    InventoryProductCreate,
    InventoryProductRead,
)
from app.services.inventory_service import InventoryService


router = APIRouter(prefix="/inventory", tags=["Inventory"])


def get_inventory_service(
    db: AsyncSession = Depends(get_db),
) -> InventoryService:
    return InventoryService(db)


@router.post(
    "/products/",
    response_model=InventoryProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    payload: InventoryProductCreate,
    current_user: AdminUser,
    service: InventoryService = Depends(get_inventory_service),
):
    try:
        return await service.create_product(current_user.hotel_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/products/", response_model=list[InventoryProductRead])
async def list_products(
    current_user: StaffUser,
    service: InventoryService = Depends(get_inventory_service),
):
    return await service.list_products(current_user.hotel_id)


@router.get("/products/{product_id}", response_model=InventoryProductRead)
async def get_product(
    product_id: int,
    current_user: StaffUser,
    service: InventoryService = Depends(get_inventory_service),
):
    product = await service.get_product_by_id(
        current_user.hotel_id, product_id
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


@router.post(
    "/movements/",
    response_model=InventoryMovementRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_movement(
    payload: InventoryMovementCreate,
    current_user: StaffUser,
    service: InventoryService = Depends(get_inventory_service),
):
    try:
        return await service.register_movement(
            current_user.hotel_id,
            current_user.id,
            payload,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc