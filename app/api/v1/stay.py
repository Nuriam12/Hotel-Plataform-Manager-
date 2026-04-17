from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import AdminUser, StaffUser
from app.schemas.stay import (
    AdditionalChargeUpdate,
    HotelSummaryResponse,
    StayAccountResponse,
    StayCreate,
    StayRead,
)
from app.services.stay_service import StayService


router = APIRouter(prefix="/stays", tags=["Stays"])


def get_stay_service(db: AsyncSession = Depends(get_db)) -> StayService:
    return StayService(db)


@router.post("/", response_model=StayRead, status_code=status.HTTP_201_CREATED)
async def check_in(
    payload: StayCreate,
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    try:
        return await service.check_in(
            current_user.hotel_id,
            current_user.id,
            payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/{stay_id}/checkout", response_model=StayRead)
async def check_out(
    stay_id: int,
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    try:
        return await service.check_out(current_user.hotel_id, stay_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/{stay_id}/additional-charge", response_model=StayRead)
async def update_additional_charge(
    stay_id: int,
    payload: AdditionalChargeUpdate,
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    try:
        return await service.update_additional_charge(
            current_user.hotel_id, stay_id, payload
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{stay_id}/account", response_model=StayAccountResponse)
async def get_account(
    stay_id: int,
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    try:
        return await service.get_account(current_user.hotel_id, stay_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/summary", response_model=HotelSummaryResponse)
async def get_summary(
    current_user: AdminUser,
    service: StayService = Depends(get_stay_service),
):
    """Resumen operativo del hotel: habitaciones, estadías activas e ingresos del mes."""
    return await service.get_summary(current_user.hotel_id)


@router.get("/", response_model=list[StayRead])
async def list_stays(
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
    status: str | None = Query(default=None, description="Filtrar por estado: active, completed"),
):
    return await service.list_stays(current_user.hotel_id, status)


@router.get("/{stay_id}", response_model=StayRead)
async def get_stay_by_id(
    stay_id: int,
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    row = await service.get_stay_by_id(current_user.hotel_id, stay_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estancia no encontrada",
        )
    return row
