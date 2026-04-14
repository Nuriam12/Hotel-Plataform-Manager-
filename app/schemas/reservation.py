from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

class ReservationCreate(BaseModel):
    room_id: int = Field(..., gt=0)
    client_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    advance_payment: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def check_dates(self) -> "ReservationCreate":
        if self.start_date >= self.end_date:
            raise ValueError("end_date debe ser posterior a start_date")
        return self


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    room_id: int
    client_id: int
    created_by: int
    start_date: date
    end_date: date
    status: str
    advance_payment: Decimal | None
    notes: str | None