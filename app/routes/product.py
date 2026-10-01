from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_admin, get_current_user
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import create_product as create_product_service, get_products
from app.services.product import get_product as get_product_service
from app.services.product import update_product as update_product_service
from app.services.product import delete_product as delete_product_service

from app.services.stock_movement import get_product_movements
from app.schemas.stock_movement import MovementType
from app.schemas.stock_movement import StockMovementResponse


router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return create_product_service(db, product_data)

@router.get("/", response_model=list[ProductResponse])
def read_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    category_id: int | None = Query(default=None, ge=1),
    is_active: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        is_active=is_active
    )

@router.get("/{product_id}/movements", response_model=list[StockMovementResponse])
def read_product_movements(
    product_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    movement_type: MovementType | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    get_product_service(db, product_id)
    
    return get_product_movements(
        db,
        product_id=product_id,
        skip=skip,
        limit=limit,
        movement_type=movement_type
    )
        
    
@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_product_service(db, product_id)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate ,db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return update_product_service(db, product_id, product_data)

@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return delete_product_service(db, product_id)