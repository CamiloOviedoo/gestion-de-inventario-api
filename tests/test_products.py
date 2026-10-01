import pytest
from pydantic import ValidationError
from fastapi import HTTPException, FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies.auth import create_access_token
from app.routes.product import router as product_router
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import create_product, get_product, get_products, update_product, delete_product
from app.services.category import delete_category

def create_test_category(db):
    category = Category(
        name="Test Category",
        description="Category for tests",
        is_active=True
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

def create_test_product(db, category_id, stock=10):
    product_data = ProductCreate(
        name="Test Product",
        description="Product for tests",
        price=100.0,
        stock=stock,
        category_id=category_id
    )
    
    return create_product(db, product_data)

def test_create_product(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id, stock=10)
    
    assert product.id is not None
    assert product.name == "Test Product"
    assert product.description == "Product for tests"
    assert product.price == 100.0
    assert product.stock == 10
    assert product.category_id == category.id
    assert product.is_active is True
    
def test_create_product_with_nonexistent_category_fails(db):
    product_data = ProductCreate(
        name="Test Product",
        description="Product for tests",
        price=100.0,
        stock=10,
        category_id=9999
    )    
    
    with pytest.raises(HTTPException) as exc:
        create_product(db, product_data)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"
    
def test_get_products_returns_active_product(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id)
    products = get_products(db)
    
    assert len(products) == 1
    assert products[0].id == product.id
    assert products[0].is_active is True
    
def test_get_product(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id)
    
    result = get_product(db, product.id)
    
    assert result.id == product.id
    assert result.name == "Test Product"
    
def test_get_nonexistent_product_fails(db):
    with pytest.raises(HTTPException) as exc:
        get_product(db, 9999)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"
    
def test_update_product(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id, stock=10)
    
    update_data = ProductUpdate(
        name="Updated Product",
        description="Updated description",
        price=150.0,
        category_id=category.id
    )
    
    updated_product = update_product(db, product.id, update_data)
    
    assert updated_product.name == "Updated Product"
    assert updated_product.description == "Updated description"
    assert updated_product.price == 150.0
    assert updated_product.category_id == category.id
    assert updated_product.stock == 10
    
def test_update_product_with_nonexistent_product_fails(db):
    category = create_test_category(db)
    
    update_data = ProductUpdate(
        name="Updated Producted",
        description="Update description",
        price=150.0,
        category_id=category.id
    ) 
    
    with pytest.raises(HTTPException) as exc:
        update_product(db, 9999, update_data)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"
    
def test_update_product_with_nonexistent_category_fails(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id) 
    
    update_data = ProductUpdate(
        name="Updated Product",
        description="Updated description",
        price=150.0,
        category_id=9999
    ) 
    
    with pytest.raises(HTTPException) as exc:
        update_product(db, product.id, update_data)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"
    
def test_delete_product_soft_deletes_product(db):
    category = create_test_category(db)
    
    product = create_test_product(db, category.id)
    
    deleted_product = delete_product(db, product.id)
    
    assert deleted_product.id == product.id
    assert deleted_product.is_active is False
    
    products = get_products(db)
    
    assert product.id not in [p.id for p in products]
    
def test_delete_nonexistent_product_fails(db):
    with pytest.raises(HTTPException) as exc:
        delete_product(db, 9999)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"
    
def test_product_create_rejects_negative_price():
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Test Product",
            description="Product for tests",
            price=-1,
            stock=10,
            category_id=1
        )
        
def test_product_create_rejects_negative_stock():
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Test product",
            description="Product for tests",
            price=100,
            stock=-1,
            catgory_id=1
        )
    
def test_product_update_does_not_accept_stock():
    updated_data = ProductUpdate(
        name="Updated Product",
        description="Updated description",
        price=150.0,
        category_id=1,
        stock=999
    ) 
    
    assert not hasattr(updated_data, "stock")                                             
    
    
def create_test_user(db, username="testuser", email="test@example.com"):
    user_data = UserCreate(
        username=username,
        email=email,
        password="secret123"
    )
    
    return create_user(db, user_data)

def create_test_app(db):
    app = FastAPI()
    
    app.include_router(product_router)
    
    def override_get_db():
        yield db
        
    app.dependency_overrides[get_db] = override_get_db
    
    return app

def test_get_products_requires_authentication(db):
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/products/")
    
    assert response.status_code == 401
    
def test_get_products_with_authenticated_user(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/products/", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    
def test_create_product_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/products/", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Product",
            "description": "Product created by test",
            "price": 100,
            "stock": 10,
            "category_id": category.id
        }
    )
    
    assert response.status_code == 403
    
def test_create_product_with_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/products/", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Product",
            "description": "Product created by test",
            "price": 100,
            "stock": 10,
            "category_id": category.id
        }
    )
    
    assert response.status_code == 201
    
    data = response.json()
    
    assert data["name"] == "New Product"
    assert data["stock"] == 10     

def test_update_product_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})    
    
    category = create_test_category(db)
    product = create_test_product(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.put(
        f"/products/{product.id}", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Product",
            "description": "updated description",
            "price": 100,
            "category_id": category.id
        }
    )
    
    assert response.status_code == 403
    
def test_update_product_with_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    product = create_test_product(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.put(
        f"/products/{product.id}", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 150,
            "category_id": category.id
        }
    )
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["name"] == "Updated Product"
    assert data["price"] == 150
 
def test_delete_product_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    product = create_test_product(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.delete(
        f"/products/{product.id}", headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
        
def test_delete_product_with_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    product = create_test_product(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.delete(
        f"/products/{product.id}", headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["id"] == product.id
    assert data["is_active"] is False       

def test_create_product_with_inactive_category_fails(db):
    category = create_test_category(db)
    
    category.is_active = False
    db.commit()
    db.refresh(category)
    
    product_data = ProductCreate(
        name="Product with inactive category",
        description="This should fail",
        price=100,
        stock=10,
        
        category_id=category.id
    )    
     
    with pytest.raises(HTTPException) as exc:
        create_product(db, product_data)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"    
    
def test_update_product_with_inactive_category_fails(db):
    category = create_test_category(db)
    
    product_data = ProductCreate(
        name="Test Product",
        description="Product for testing",
        price=100,
        stock=10,
        
        category_id=category.id
    )
    
    product = create_product(db, product_data)
    
    category.is_active = False
    db.commit()
    db.refresh(category)
    
    updated_data = ProductUpdate(
        name="Updated Product",
        description="Updated description",
        price=150,
        
        category_id=category.id
    )
    
    with pytest.raises(HTTPException) as exc:
        update_product(db, product.id, updated_data)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"    