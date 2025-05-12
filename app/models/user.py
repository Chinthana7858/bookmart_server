from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    address = Column(String(100))
    role = Column(String(100), default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")