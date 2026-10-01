from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: str
    

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)    
    
class CategoryUpdate(BaseModel):
    name: str
    description: str    