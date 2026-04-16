from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import AdminUser, StaffUser
from app.schemas.room import RoomCreate, RoomRead
from app.services.room_service import RoomService


router = APIRouter(prefix="/rooms", tags=["Rooms"])

def get_room_service(db: AsyncSession = Depends(get_db)) -> RoomService:
    return RoomService(db)

@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreate,
    current_user: AdminUser,
    service: RoomService = Depends(get_room_service),
):
    try: 
        room = await service.create(current_user.hotel_id, payload)
    except ValueError as exc : 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return room 

@router.get("/", response_model=list[RoomRead])
async def list_rooms( #con esto estamos listando las habitaciones
    current_user : StaffUser,
    service: RoomService = Depends(get_room_service),
):
    return await service.list_rooms(current_user.hotel_id) 

@router.get("/{room_id}", response_model=RoomRead)
async def get_room_by_id( #con esto estamos obteniendo una habitacion por su id
    room_id: int,
    current_user : StaffUser,
    service: RoomService = Depends(get_room_service),
):
    room = await service.get_room_by_id(current_user.hotel_id, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitacion no encontrada")
    return room 

