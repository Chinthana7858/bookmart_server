from pydantic import BaseModel
from datetime import datetime

class RecommendationOut(BaseModel):
    base_product_id: int
    recommended_product_id: int
    score: int
    created_at: datetime

    class Config:
        from_attributes = True


