from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class RoomCreate(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20)
    floor: str = Field(..., min_length=1, max_length=20)
    room_type: str = Field(..., min_length=1, max_length=20)
    price_per_night: Decimal = Field(gt=0, multiple_of=10, decimal_places=2)


class RoomUpdate(BaseModel):
    floor: str | None = Field(default=None, min_length=1, max_length=20)
    room_type: str | None = Field(default=None, min_length=1, max_length=20)
    price_per_night: Decimal | None = Field(default=None, gt=0, decimal_places=2)


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    room_number: str
    floor: str
    room_type: str
    price_per_night: Decimal
    status: str
