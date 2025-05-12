from sqlalchemy import Column, Integer, String, Text
from app.db import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")