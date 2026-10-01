from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, product_data: ProductCreate):
    category = (db.query(Category).filter(Category.id == product_data.category_id, Category.is_active.is_(True)).first())
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category_id=product_data.category_id, is_active=True
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product
    
def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category_id: int | None = None,
    is_active: bool = True
):
    query = db.query(Product).filter(Product.is_active.is_(is_active))
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    return query.offset(skip).limit(limit).all()
    
        
def get_product(db: Session, product_id: int):
    product = (db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first())
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product     

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    product = (db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first())  
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    category = (db.query(Category).filter(Category.id == product_data.category_id, Category.is_active.is_(True)).first())
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.category_id = product_data.category_id
    
    db.commit()
    db.refresh(product)
    
    return product

def delete_product(db: Session, product_id: int):
    product = (db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first())
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    
    db.commit()
    db.refresh(product)
    
    return product