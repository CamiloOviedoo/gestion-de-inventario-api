from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum


class MovementType(str, Enum):
    ENTRADA = "entrada",
    SALIDA = "salida"
    
        
class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int = Field(gt=0)
   
    
class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: int 
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)    