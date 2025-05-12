
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")