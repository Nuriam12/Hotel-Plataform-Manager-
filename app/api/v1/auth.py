from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)  
async def login(
    credentials: LoginRequest, #esto es lo que nos envia el cliente para iniciar sesion
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db) 
    user = await repo.get_by_hotel_and_username(  #esto es para obtener el usuario por el hotel y el username
        credentials.hotel_id, credentials.username,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "hotel_id": user.hotel_id,
            "role": user.role,
            "username": user.username,
        }
    )
    return TokenResponse(access_token=access_token)
