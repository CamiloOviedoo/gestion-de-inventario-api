from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.models.user import User
from app.schemas.user import UserCreate

password_hash = PasswordHash.recommended()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate):
    hashed_password = password_hash.hash(user_data.password)
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        role="user"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user