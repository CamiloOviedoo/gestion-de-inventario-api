from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import StockMovementCreate, MovementType

def create_stock_movement(db: Session, movement: StockMovementCreate):
    try:
        product = db.query(Product).filter(Product.id == movement.product_id).first()
    
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
        if movement.movement_type == MovementType.SALIDA:
            if product.stock < movement.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
        
            product.stock -= movement.quantity
    
        else:
            product.stock += movement.quantity
        
        stock_movement = StockMovement(product_id=movement.product_id, movement_type=movement.movement_type.value, quantity=movement.quantity)
    
        db.add(stock_movement)
        db.commit()
        db.refresh(stock_movement)
        return stock_movement
       
    except HTTPException:
        db.rollback()
        raise 
    
    except Exception:
        db.rollback()
        raise


def get_stock_movements(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    product_id: int | None = None,
    movement_type: MovementType | None = None
):
    query = db.query(StockMovement)
    
    if product_id is not None:
        query = query.filter(StockMovement.product_id == product_id)
    
    if movement_type is not None:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    return query.offset(skip).limit(limit).all()

def get_product_movements(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 10,
    movement_type: MovementType | None = None
):
    query = db.query(StockMovement).filter(StockMovement.product_id == product_id)
    
    if movement_type is not None:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    return query.offset(skip).limit(limit).all()
    

def get_stock_movement(db: Session, movement_id: int):
    movement = db.query(StockMovement).filter(StockMovement.id == movement_id).first()
    
    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")
    
    return movement