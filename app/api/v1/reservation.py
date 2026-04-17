from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import StaffUser
from app.core.database import get_db
from app.services.reservation_service import ReservationService
from app.schemas.reservation import ReservationCreate, ReservationRead

router = APIRouter(prefix="/reservations", tags=["Reservations"])

def get_reservation_service(db: AsyncSession = Depends(get_db)) -> ReservationService:
    return ReservationService(db)

@router.post("/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate,
    current_user : StaffUser,
    service: ReservationService = Depends(get_reservation_service),
):
    try:
        reservation = await service.create(current_user.hotel_id, current_user.id, payload)
    except LookupError as exc : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc : 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return reservation

@router.get("/", response_model=list[ReservationRead])
async def list_reservations(
    current_user : StaffUser,
    service: ReservationService = Depends(get_reservation_service),
):

    return await service.list_reservations(current_user.hotel_id)

@router.get("/{reservation_id}", response_model=ReservationRead)
async def get_reservation_by_id(
    reservation_id: int,
    current_user : StaffUser,
    service: ReservationService = Depends(get_reservation_service),
):
    row = await service.get_reservation_by_id(current_user.hotel_id, reservation_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return row


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
async def cancel_reservation(
    reservation_id: int,
    current_user: StaffUser,
    service: ReservationService = Depends(get_reservation_service),
):
    try:
        return await service.cancel_reservation(current_user.hotel_id, reservation_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc