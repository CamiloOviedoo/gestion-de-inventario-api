from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String,unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String, default="user", nullable=False)
    