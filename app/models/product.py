from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    is_active = Column(Boolean)
    category_id = Column(ForeignKey("category.id"))
    category = relationship("Category", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product")