from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class StayCreate(BaseModel):
    room_id: int = Field(..., gt=0)
    client_id: int = Field(..., gt=0)
    reservation_id: int | None = Field(default=None, gt=0)
    price_per_night: float = Field(..., gt=0)
    notes: str | None = Field(default=None, max_length=5000)
    checkin_datetime: datetime | None = Field(default=None)

class StayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    room_id: int
    client_id: int
    reservation_id: int | None
    created_by: int
    checkin_datetime: datetime
    checkout_datetime: datetime | None
    price_per_night: float
    status: str
    notes: str | None

