from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine( #creamos el motor de la base de datos
    settings.DATABASE_URL, 
    echo=settings.ENVIRONMENT == "development"
    )

AsyncSessionLocal = async_sessionmaker(engine, #creamos el sessionmaker para la base de datos
    class_=AsyncSession,
    expire_on_commit=False, 
    )

class Base(DeclarativeBase): #creamos la base para las tablas de la base de datos
    pass

async def get_db(): #creamos la funcion para obtener la session de la base de datos
    async with AsyncSessionLocal() as session:
        yield session