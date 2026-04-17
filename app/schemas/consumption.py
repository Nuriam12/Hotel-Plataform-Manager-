from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class ClientConsumptionCreate(BaseModel):
    stay_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    notes: str | None = Field(default=None, max_length=5000)

class ClientConsumptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    stay_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    created_at: datetime
    is_cancelled: bool
    cancelled_at: datetime | None
    cancelled_by: int | None