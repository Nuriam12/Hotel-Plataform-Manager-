from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db 
        
    async def get_by_hotel_and_username(
        self, hotel_id:int, username:str
    ) -> User | None:
        result = await self.db.execute(select(User).where(
            User.hotel_id == hotel_id,
            User.username == username,
            User.is_active == True,
        ))
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id:int) -> User | None:
        result = await self.db.execute(select(User).where(
            User.id == user_id,
        ))
        return result.scalar_one_or_none()