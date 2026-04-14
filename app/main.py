from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1.auth import router as auth_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.client import router as client_router
from app.api.v1.reservation import router as reservation_router
from app.api.v1.stay import router as stay_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.consumption import router as consumption_router

app = FastAPI( #con esto levantamos FASTAPI
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc", 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(client_router, prefix="/api/v1")
app.include_router(reservation_router, prefix="/api/v1")
app.include_router(stay_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(consumption_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )