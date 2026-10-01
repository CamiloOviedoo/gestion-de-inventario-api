from sqlalchemy.orm import Session

from app.models.user import User
from app.services.user import get_user_by_username
from app.services.user import create_user
from app.schemas.user import UserCreate

def create_initial_admin(
    db: Session,
    username: str,
    email: str,
    password: str
) -> User:
    existing_user = get_user_by_username(db, username)
    
    if existing_user:
        return existing_user
    
    admin_data = UserCreate(
        username=username,
        email=email,
        password=password
    )
    
    user = create_user(db, admin_data)
    
    user.role = "admin"
    
    db.commit()
    db.refresh(user)
    
    return user
