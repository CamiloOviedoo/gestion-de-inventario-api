from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def create_category(db: Session, category_data: CategoryCreate):
    category = Category(name=category_data.name, description=category_data.description, is_active=True)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    is_active: bool = True
):
    return (db.query(Category)).filter(Category.is_active.is_(is_active)).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    category = (db.query(Category).filter(Category.id == category_id, Category.is_active.is_(True)).first())
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category
    
def update_category(db: Session, category_id: int, category_data: CategoryUpdate):
    category = (db.query(Category).filter(Category.id == category_id, Category.is_active.is_(True)).first())
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.name = category_data.name
    category.description = category_data.description
    
    db.commit()
    db.refresh(category)
    
    return category

def delete_category(db: Session, category_id: int):
    category = (db.query(Category).filter(Category.id == category_id, Category.is_active.is_(True)).first())
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.is_active = False
    
    db.commit()
    db.refresh(category)
    
    return category