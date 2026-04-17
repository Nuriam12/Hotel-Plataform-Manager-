from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------------------------------------ #
# Check-in                                                             #
# ------------------------------------------------------------------ #

class StayCreate(BaseModel):
    room_id: int = Field(..., gt=0)
    client_id: int = Field(..., gt=0)
    reservation_id: int | None = Field(default=None, gt=0)
    price_per_night: Decimal = Field(..., gt=0, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)
    checkin_datetime: datetime | None = Field(default=None)


# ------------------------------------------------------------------ #
# Respuesta básica de stay (para check-in, check-out, listados)        #
# ------------------------------------------------------------------ #

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
    price_per_night: Decimal
    status: str
    notes: str | None
    account_number: int | None
    additional_charge: Decimal | None
    additional_charge_notes: str | None


# ------------------------------------------------------------------ #
# Cargo adicional (ADIC)                                               #
# ------------------------------------------------------------------ #

class AdditionalChargeUpdate(BaseModel):
    additional_charge: Decimal = Field(..., ge=0, decimal_places=2)
    additional_charge_notes: str | None = Field(default=None, max_length=5000)


# ------------------------------------------------------------------ #
# Tablero de habitaciones                                              #
# ------------------------------------------------------------------ #

class ActiveStaySummary(BaseModel):
    stay_id: int
    account_number: int | None
    client_name: str
    client_dni: str
    checkin_datetime: datetime
    nights_so_far: int
    total_estimate: Decimal


class RoomBoardItem(BaseModel):
    id: int
    room_number: str
    floor: str
    room_type: str
    price_per_night: Decimal
    status: str
    active_stay: ActiveStaySummary | None = None


# ------------------------------------------------------------------ #
# Cuenta corriente completa                                            #
# ------------------------------------------------------------------ #

class StayInfo(BaseModel):
    id: int
    status: str
    checkin_datetime: datetime
    checkout_datetime: datetime | None
    price_per_night: Decimal
    notes: str | None
    additional_charge: Decimal | None
    additional_charge_notes: str | None


class RoomInfo(BaseModel):
    id: int
    room_number: str
    room_type: str
    floor: str


class ClientInfo(BaseModel):
    id: int
    name: str
    dni: str
    phone: str | None


class ConsumptionLine(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime
    is_cancelled: bool


class AccountTotals(BaseModel):
    nights: int
    nights_cost: Decimal
    consumptions_total: Decimal
    additional_charge: Decimal
    grand_total: Decimal


class StayAccountResponse(BaseModel):
    account_number: int | None
    stay: StayInfo
    room: RoomInfo
    client: ClientInfo
    consumptions: list[ConsumptionLine]
    totals: AccountTotals
