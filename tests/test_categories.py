import pytest
from pydantic import ValidationError
from fastapi import HTTPException, FastAPI 
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies.auth import create_access_token
from app.routes.category import router as category_router
from app.schemas.user import UserCreate
from app.services.user import create_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import create_category, get_categories, get_category, update_category, delete_category


def create_test_category(db):
    category_data = CategoryCreate(
        name="Test Category",
        description="Category for tests"
    )
    
    return create_category(db, category_data)

def test_create_category(db):
    category = create_test_category(db)
    
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Category for tests"
    assert category.is_active is True
    
def test_get_categories_returns_active_categories(db):
    category = create_test_category(db)
    
    categories = get_categories(db)
    
    assert len(categories) == 1
    assert categories[0].id == category.id
    assert categories[0].is_active is True
    
def test_get_category(db):
    category = create_test_category(db)
    
    result = get_category(db, category.id)
    
    assert result.id == category.id
    assert result.name == "Test Category"
    assert result.description == "Category for tests"
    
def test_get_nonexistent_category_fails(db):
    with pytest.raises(HTTPException) as exc:
        get_category(db, 9999)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"
    
def test_update_category(db):
    category = create_test_category(db)
    
    update_data = CategoryUpdate(
        name="Updated Category",
        description= "Updated description"
    )
    
    updated_category = update_category(db, category.id, update_data)
    
    assert updated_category.id == category.id
    assert updated_category.name == "Updated Category"
    assert updated_category.description == "Updated description"
    assert updated_category.is_active is True
    
def test_update_nonexistent_category_fails(db):
    update_data = CategoryUpdate(
        name="Updated Category",
        description="Updated description"
    )    
    
    with pytest.raises(HTTPException) as exc:
        update_category(db, 9999, update_data)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"

def test_delete_category_soft_deletes_category(db):
    category = create_test_category(db)
    
    deleted_category = delete_category(db, category.id)
    
    assert deleted_category.id == category.id
    assert deleted_category.is_active is False
    
    categories = get_categories(db)
    
    assert category.id not in [c.id for c in categories]
    
def test_delete_nonexistent_category_fails(db):
    with pytest.raises(HTTPException) as exc:
        delete_category(db, 9999)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Category not found"
    
def test_create_category_has_no_products_by_default(db):
    category = create_test_category(db)
    
    assert category.products == []

def create_test_user(db, username="testuser", email="test@example.com"):
    user_data = UserCreate(
        username=username,
        email=email,
        password="secret123"
    )
    
    return create_user(db, user_data)

def create_test_app(db):
    app = FastAPI()
    
    app.include_router(category_router)
    
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app 

def test_get_categories_requires_authentication(db):
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/category/")
    
    assert response.status_code == 401
    
def test_create_category_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/category/", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Category",
            "description": "Category created by test"
        }
    )
    
    assert response.status_code == 403

def test_create_category_with_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/category/", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Category",
            "description": "Category created by test"
        }
    )
    
    assert response.status_code == 201
    
def test_update_category_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.put(
        "/category/", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Category",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 403
    
def test_delete_category_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    category = create_test_category(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.delete(
        f"/category/{category.id}", headers={"Authorization": f"Bearer {token}"} 
    )
    
    assert response.status_code == 403          
    
def test_get_deleted_category_returns_404(db):
    category = create_test_category(db)
    
    user = create_test_user(db)
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    delete_category(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get(
        f"/category/{category.id}", headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    
def test_update_deleted_category_returns_404(db):
    category = create_test_category(db)
    
    user = create_test_user(db)
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    delete_category(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.put(
        f"/category/{category.id}", headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Category",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    

def test_delete_deleted_category_returns_404(db):
    category = create_test_category(db)
    
    user = create_test_user(db)
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    delete_category(db, category.id)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.delete(
        f"/category/{category.id}", headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
