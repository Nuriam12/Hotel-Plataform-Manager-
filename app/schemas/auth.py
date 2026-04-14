from pydantic import BaseModel

class LoginRequest(BaseModel):
    hotel_id: int
    username: str
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    user_id: int
    hotel_id: int
    role: str
    username: str
    
