from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    base_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    recommended_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


    base_product = relationship("Product", foreign_keys=[base_product_id], passive_deletes=True)
    recommended_product = relationship("Product", foreign_keys=[recommended_product_id], passive_deletes=True)