import jwt
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user import get_user_by_username
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES 

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode an access token and validate its required subject claim."""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credential_exception

    if not isinstance(payload, dict) or not payload.get("sub"):
        raise credential_exception

    return payload

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    
    if not user:
        return None
    
    from app.services.user import password_hash
    
    if not password_hash.verify(password, user.hashed_password):
        return None
    
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    payload = decode_access_token(token)
    username = payload["sub"]
    
    user = get_user_by_username(db, username)
    
    if user is None:
        raise credential_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    return user     

def require_role(required_role: str, detail: str = "Insufficient permissions"):
    def role_dependency(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        
        return current_user
    return role_dependency

get_current_admin = require_role("admin", detail="Admin privileges required")            
