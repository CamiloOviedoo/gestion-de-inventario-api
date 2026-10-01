import pytest
import jwt
from fastapi import HTTPException, FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.routes.auth import router as auth_router
from app.dependencies.auth import authenticate_user, create_access_token, get_current_user, get_current_admin, SECRET_KEY, ALGORITHM, require_role
from app.schemas.user import UserCreate
from app.services.user import create_user, get_user_by_email, get_user_by_username, password_hash


def create_test_user(db, username="testuser", email="test@example.com", password="secret123"):
    user_data = UserCreate(
        username=username,
        email=email,
        password=password
    )
    
    return create_user(db, user_data)

def create_test_app(db):
    app = FastAPI()
    
    app.include_router(auth_router)
    
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app
        
def test_create_user(db):
    user = create_test_user(db)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.role == "user"
    
def test_password_is_hashed(db):
    user = create_test_user(db)
    
    assert user.hashed_password != "secret123"
    assert password_hash.verify("secret123", user.hashed_password)
    
def test_get_user_by_username(db):
    user = create_test_user(db)
    
    result = get_user_by_username(db, "testuser")
    
    assert result is not None
    assert result.id == user.id
    
def test_get_user_by_email(db):
    user = create_test_user(db)
    
    result = get_user_by_email(db, "test@example.com")
    
    assert result is not None
    assert result.id == user.id
    
def test_authenticate_user_wrong_password(db):
    create_test_user(db)
    
    result = authenticate_user(db, "testuser", "wrongpassword")
    
    assert result is None
    
def test_authenticate_nonexistent_user(db):
    result = authenticate_user(db, "doesnotexist", "secret123")
    
    assert result is None
    
def test_create_access_token():
    token = create_access_token({"sub": "testuser"})
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
def test_get_current_user_with_valid_token(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    current_user = get_current_user(token=token, db=db)    
    
    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.username == user.username
    
def test_get_current_with_invalid_token(db):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid-token", db=db) 
    
    assert exc_info.value.status_code == 401

def test_get_current_user_with_nonexistent_user(db):
    token = create_access_token({"sub": "doesnotexist"})
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)
        
    assert exc_info.value.status_code == 401

def test_get_current_user_with_inactive_user(db):
    user = create_test_user(db)
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)
        
    assert exc_info.value.status_code == 403        
    
def test_authenticate_user_success(db):
    user = create_test_user(db)
    
    result = authenticate_user(db, "testuser", "secret123")
    
    assert result is not None
    assert result.id == user.id
    assert result.username == user.username                                     
    
def test_auth_me_with_valid_token(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == "user"
    
    assert "password" not in data
    assert "hashed_password" not in data
    
def test_auth_me_without_token(db):
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/auth/me")
    
    assert response.status_code == 401
    
def test_auth_me_with_invalid_token(db):
    app = create_test_app(db)
    client = TestClient(app) 
    
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    
    assert response.status_code == 401

def test_auth_me_with_nonexistent_user(db):
    token = create_access_token({"sub": "doesnotexist"})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer{token}"})
    
    assert response.status_code == 401
    
def test_auth_me_with_inactive_user(db):
    user = create_test_user(db)
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    app = create_test_app(db)
    client = TestClient(app)
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403              
    
def test_get_current_admin_with_admin_user(db):
    user = create_test_user(db)
    
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username}) 
    
    current_user = get_current_user(token=token, db=db)
    
    admin = get_current_admin(current_user=current_user)
    
    assert admin.id == user.id
    assert admin.role == "admin"
    
def test_get_current_admin_with_regular_user(db):
    user = create_test_user(db)
    
    token = create_access_token({"sub": user.username})
    
    current_user = get_current_user(token=token, db=db)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_admin(current_user=current_user)
        
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admin privileges required" 
    
def test_get_current_admin_with_inactive_admin(db):
    user = create_test_user(db)
    
    user.role = "admin"
    user.is_active = False
    
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"  
    
def test_get_current_user_with_expired_token(db):
    user = create_test_user(db)
    
    token = jwt.encode({
        "sub": user.username,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }, SECRET_KEY, algorithm=ALGORITHM
    )
    
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)
        
    assert exc.value.status_code == 401

def test_get_current_user_without_sub(db):
    token = create_access_token({"username": "testuser"})
    
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)
        
    assert exc.value.status_code == 401        
 
def test_require_role_allows_matching_role(db):
    user = create_test_user(db)
    user.role = "manager"
    
    db.commit()
    db.refresh(user)
    
    dependency = require_role("manager")
    
    result = dependency(current_user=user)
    
    assert result == result
    
def test_require_role_rejects_wrong_role(db):
    user = create_test_user(db)
    
    dependency = require_role("admin")
    
    with pytest.raises(HTTPException) as exc:
        dependency(current_user=user)
        
    assert exc.value.status_code == 403
    assert exc.value.detail == "Insufficient permissions"        
                             