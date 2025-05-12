
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserActivityCreate(BaseModel):
    product_id: int
    action: str

class UserActivityResponse(UserActivityCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # For Pydantic v2
