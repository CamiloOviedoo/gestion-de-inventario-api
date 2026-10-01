from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stock_movement import StockMovementCreate
from app.services.stock_movement import create_stock_movement, get_stock_movement, get_stock_movements
from app.dependencies.auth import get_current_user, get_current_admin

router = APIRouter(
    prefix="",
    tags=["Stock Movements"]
) 

@router.post("/stock-movement")
def create_movement(movement: StockMovementCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return create_stock_movement(db, movement)

@router.get("/stock-movement")
def read_movements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    product_id: int | None = Query(default=None, ge=1),
    movement_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_stock_movements(db, skip=skip, limit=limit, product_id=product_id, movement_type=movement_type)

@router.get("/stock-movements/")
def read_movements_legacy(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_stock_movements(db)

@router.get("/stock-movement/{movement_id}")
def read_movement(movement_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_stock_movement(db, movement_id)