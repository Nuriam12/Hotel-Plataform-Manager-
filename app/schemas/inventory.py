from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class InventoryProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)

class InventoryProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    hotel_id: int
    name: str
    category: str | None
    current_stock: int

class InventoryMovementCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    kind: Literal["in", "out"]
    quantity: int = Field(..., gt=0)
    notes: str | None = Field(default=None, max_length=5000)

class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    product_id: int
    created_by: int
    quantity: int
    notes: str | None
    movement_type: str = Field(validation_alias="type")
