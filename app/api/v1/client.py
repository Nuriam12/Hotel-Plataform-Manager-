from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependency import StaffUser
from app.core.database import get_db
from app.services.client_service import ClientService
from app.schemas.client import ClientCreate, ClientRead


router = APIRouter(prefix="/clients", tags=["Clients"])

def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService(db)

@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    current_user : StaffUser,
    service: ClientService = Depends(get_client_service),
):
    try:
        client = await service.create(current_user.hotel_id, payload)
    except ValueError as exc : 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return client

@router.get("/", response_model=list[ClientRead])
async def list_clients(
    current_user : StaffUser,
    service: ClientService = Depends(get_client_service),
):
    return await service.list_clients(current_user.hotel_id)

@router.get("/search", response_model=list[ClientRead])
async def search_clients_by_dni(
    dni: str,
    current_user : StaffUser,
    service: ClientService = Depends(get_client_service),
):
    clients = await service.search_clients_by_dni(current_user.hotel_id, dni)
    if not clients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clientes no encontrados")
    return clients

@router.get("/{client_id}", response_model=ClientRead)
async def get_client_by_id(
    client_id: int,
    current_user : StaffUser,
    service: ClientService = Depends(get_client_service),
):
    client = await service.get_client_by_id(current_user.hotel_id, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return client