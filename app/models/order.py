from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False,)
    order_date = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"),)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items") 
    product = relationship("Product")