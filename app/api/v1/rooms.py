from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import AdminUser, StaffUser
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.schemas.stay import RoomBoardItem
from app.services.room_service import RoomService
from app.services.stay_service import StayService


router = APIRouter(prefix="/rooms", tags=["Rooms"])


def get_room_service(db: AsyncSession = Depends(get_db)) -> RoomService:
    return RoomService(db)


def get_stay_service(db: AsyncSession = Depends(get_db)) -> StayService:
    return StayService(db)


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreate,
    current_user: AdminUser,
    service: RoomService = Depends(get_room_service),
):
    try:
        room = await service.create(current_user.hotel_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return room


@router.patch("/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: int,
    payload: RoomUpdate,
    current_user: AdminUser,
    service: RoomService = Depends(get_room_service),
):
    try:
        return await service.update_room(current_user.hotel_id, room_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/board", response_model=list[RoomBoardItem])
async def get_board(
    current_user: StaffUser,
    service: StayService = Depends(get_stay_service),
):
    """Tablero de habitaciones: estado completo del hotel en tiempo real."""
    return await service.get_board(current_user.hotel_id)


@router.get("/", response_model=list[RoomRead])
async def list_rooms(
    current_user: StaffUser,
    service: RoomService = Depends(get_room_service),
):
    return await service.list_rooms(current_user.hotel_id)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room_by_id(
    room_id: int,
    current_user: StaffUser,
    service: RoomService = Depends(get_room_service),
):
    room = await service.get_room_by_id(current_user.hotel_id, room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habitacion no encontrada"
        )
    return room
