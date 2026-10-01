from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str