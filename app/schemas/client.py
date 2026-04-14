from pydantic import BaseModel, Field, ConfigDict


class ClientCreate(BaseModel): 
    dni: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, min_length=1, max_length=20)

class ClientRead(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    id: int
    dni: str
    name: str
    phone: str | None

