from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.product import ProductOut
from app.schemas.user import UserResponse

class OrderCreate(BaseModel):
    user_id: int


class OrderItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int

    class Config:
        from_attributes = True

class OrderOut(OrderCreate):
    id: int
    user: UserResponse    
    order_date: datetime
    items: Optional[List[OrderItemOut]] = []

    class Config:
        from_attributes = True



class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

