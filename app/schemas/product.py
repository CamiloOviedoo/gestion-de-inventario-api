from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    category_id: int
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    is_active: bool
    category_id: int
    
    model_config = ConfigDict(from_attributes=True)    
    
class ProductUpdate(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    category_id: int