from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import authenticate_user, create_access_token, get_current_user
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.user import create_user, get_user_by_username, get_user_by_email

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_user(db, user_data)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}    

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user