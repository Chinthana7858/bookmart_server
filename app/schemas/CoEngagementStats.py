from pydantic import BaseModel
from datetime import datetime

class CoEngagementStatsOut(BaseModel):
    id: int
    product_id_a: int
    product_id_b: int
    co_view_count: int
    co_add_cart_count: int
    co_buy_count: int
    last_updated: datetime

    class Config:
        from_attributes = True  # for Pydantic v2+ compatibility with SQLAlchemy
