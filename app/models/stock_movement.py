from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movement"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    movement_type = Column(String)
    quantity = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    product = relationship("Product", back_populates="stock_movements")
    