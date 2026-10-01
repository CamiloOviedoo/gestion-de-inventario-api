from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    products = relationship("Product", back_populates="category")
    