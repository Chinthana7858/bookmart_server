from sqlalchemy import Column, ForeignKey, Integer, DateTime
from datetime import datetime
from app.db import Base

class CoEngagementStats(Base):
    __tablename__ = "co_engagement_stats"

    id = Column(Integer, primary_key=True, index=True)
    product_id_a = Column(Integer,ForeignKey("products.id"), index=True)
    product_id_b = Column(Integer,ForeignKey("products.id"), index=True,)
    co_view_count = Column(Integer, default=0)
    co_add_cart_count = Column(Integer, default=0)
    co_buy_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
