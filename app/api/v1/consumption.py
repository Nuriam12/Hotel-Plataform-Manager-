from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependency import StaffUser
from app.schemas.consumption import ClientConsumptionCreate, ClientConsumptionRead
from app.services.consumption_service import ConsumptionService


router = APIRouter(prefix="/consumptions", tags=["Consumptions"])


def get_consumption_service(
    db: AsyncSession = Depends(get_db),
) -> ConsumptionService:
    return ConsumptionService(db)


@router.post(
    "/",
    response_model=ClientConsumptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_consumption(
    payload: ClientConsumptionCreate,
    current_user: StaffUser,
    service: ConsumptionService = Depends(get_consumption_service),
):
    try:
        return await service.record_consumption(
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


@router.get("/", response_model=list[ClientConsumptionRead])
async def list_consumptions(
    current_user: StaffUser,
    service: ConsumptionService = Depends(get_consumption_service),
    stay_id: int | None = Query(default=None, gt=0),
):
    return await service.list_consumptions(
        current_user.hotel_id,
        stay_id,
    )