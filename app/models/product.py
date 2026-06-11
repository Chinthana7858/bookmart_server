from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Table
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship

product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    publisher = Column(String(150))
    author = Column(String(150))
    language = Column(String(80))
    imageUrl = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)  
    created_at = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", foreign_keys=[category_id], passive_deletes=True)
    categories = relationship(
        "Category",
        secondary=product_categories,
        back_populates="products",
        passive_deletes=True,
    )

    @property
    def category_ids(self):
        return [category.id for category in self.categories]
