from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db import Base

class UserActivity(Base):
    __tablename__ = "user_activities"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100))
    product_id = Column(Integer, ForeignKey("products.id"))
    action = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
