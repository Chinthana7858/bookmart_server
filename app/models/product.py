from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    imageUrl = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)  
    created_at = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", back_populates="products", passive_deletes=True)
