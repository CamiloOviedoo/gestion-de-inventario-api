from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.dependencies.auth import get_current_admin, get_current_user
from app.services.category import (
    create_category as create_category_service,
    get_categories,
    get_category,
    update_category as update_category_service,
    delete_category as delete_category_service
)

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data:CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return create_category_service(db, category_data)

@router.get("/", response_model=list[CategoryResponse])
def read_categories(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100), is_active: bool = Query(default=True), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_categories(db, skip=skip, limit=limit, is_active=is_active)

@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_category(db, category_id)
    
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return update_category_service(db, category_id, category_data)

@router.put("/", dependencies=[Depends(get_current_admin)])
def update_category_without_id():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category ID is required")

@router.delete("/{category_id}", response_model=CategoryResponse)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return delete_category_service(db, category_id)