from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
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
    phone_country_code = Column(String(10))
    phone_number = Column(String(30))
    birthday = Column(Date)
    gender = Column(String(30))
    role = Column(String(100), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    addresses = relationship(
        "UserAddress",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(UserAddress.is_default), UserAddress.id",
    )


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(40), nullable=False, default="Home")
    recipient_name = Column(String(100))
    phone_country_code = Column(String(10))
    phone_number = Column(String(30))
    line1 = Column(String(150), nullable=False)
    line2 = Column(String(150))
    city = Column(String(80), nullable=False)
    state = Column(String(80))
    postal_code = Column(String(30))
    country = Column(String(80), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="addresses")
