import pytest
from fastapi import HTTPException, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.database import get_db
from app.dependencies.auth import create_access_token
from app.routes.stock_movement import router as stock_movement_router
from app.schemas.user import UserCreate
from app.services.user import create_user
from app.models.category import Category
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import MovementType, StockMovementCreate
from app.services.stock_movement import create_stock_movement, get_stock_movement, get_stock_movements


def create_test_product(db, stock=10):
    category = Category(
        name="Test Category",
        description="Category for tests",
        is_active=True
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Product",
        description="Product for tests",
        price=100,
        stock=stock,
        is_active=True,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def test_create_entry_increases_stock(db):
    product = create_test_product(db, stock=10)

    movement = StockMovementCreate(
        product_id=product.id,
        movement_type=MovementType.ENTRADA,
        quantity=5
    )

    result = create_stock_movement(db, movement)

    db.refresh(product)

    assert result.product_id == product.id
    assert result.movement_type == "entrada"
    assert result.quantity == 5
    assert product.stock == 15


def test_create_exit_decreases_stock(db):
    product = create_test_product(db, stock=10)

    movement = StockMovementCreate(
        product_id=product.id,
        movement_type=MovementType.SALIDA,
        quantity=4
    )

    result = create_stock_movement(db, movement)

    db.refresh(product)

    assert result.movement_type == "salida"
    assert result.quantity == 4
    assert product.stock == 6


def test_exit_with_insufficient_stock_fails(db):
    product = create_test_product(db, stock=5)

    movement = StockMovementCreate(
        product_id=product.id,
        movement_type=MovementType.SALIDA,
        quantity=10
    )

    with pytest.raises(HTTPException) as error:
        create_stock_movement(db, movement)

    assert error.value.status_code == 400
    assert error.value.detail == "Insufficient stock"

    db.refresh(product)

    assert product.stock == 5


def test_movement_for_nonexistent_product_fails(db):
    movement = StockMovementCreate(
        product_id=9999,
        movement_type=MovementType.ENTRADA,
        quantity=5
    )

    with pytest.raises(HTTPException) as error:
        create_stock_movement(db, movement)

    assert error.value.status_code == 404
    assert error.value.detail == "Product not found"


def test_zero_quantity_is_rejected():
    with pytest.raises(ValidationError):
        StockMovementCreate(
            product_id=2,
            movement_type=MovementType.ENTRADA,
            quantity=0
        )


def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        StockMovementCreate(
            product_id=2,
            movement_type=MovementType.ENTRADA,
            quantity=-5
        )


def test_invalid_movement_type_is_rejected():
    with pytest.raises(ValueError):
        StockMovementCreate(
            product_id=2,
            movement_type="banana",
            quantity=5
        )


def test_get_stock_movements(db):
    product = create_test_product(db, stock=10)

    movement1 = StockMovement(
        product_id=product.id,
        movement_type="entrada",
        quantity=5
    )

    movement2 = StockMovement(
        product_id=product.id,
        movement_type="salida",
        quantity=2
    )

    db.add_all([movement1, movement2])
    db.commit()

    movements = get_stock_movements(db)

    assert len(movements) == 2


def test_get_stock_movement(db):
    product = create_test_product(db)

    movement = StockMovement(
        product_id=product.id,
        movement_type="entrada",
        quantity=5
    )

    db.add(movement)
    db.commit()
    db.refresh(movement)

    result = get_stock_movement(db, movement.id)

    assert result.id == movement.id
    assert result.product_id == product.id
    assert result.quantity == 5


def test_get_nonexistent_stock_movement_fails(db):
    with pytest.raises(HTTPException) as error:
        get_stock_movement(db, 9999)

    assert error.value.status_code == 404
    assert error.value.detail == "Stock movement not found"

def create_test_user(db, username="testuser", email="test@example.com"):
    user_data = UserCreate(
        username=username,
        email=email,
        password="secret123"
    )    
    
    return create_user(db, user_data)

def create_test_app(db):
    app = FastAPI()
    
    app.include_router(stock_movement_router)
    
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app

def test_get_stock_movements_requires_authentication(db):
    app = create_test_app(db) 
    client = TestClient(app)
    
    response = client.get("/stock-movements/")
    
    assert response.status_code == 401
    
def test_create_stock_movement_requires_admin(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    product = create_test_product(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/stock-movement/", headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product.id,
            "movement_type": "entrada",
            "quantity": 5
        }
    )
    
    assert response.status_code == 403
    
def test_create_stock_movement_with_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    product = create_test_product(db)
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.post(
        "/stock-movement/", headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product.id,
            "movement_type": "entrada",
            "quantity": 5
        }
    ) 
    
    assert response.status_code == 200
    