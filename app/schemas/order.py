from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.schemas.product import ProductOut
from app.schemas.user import UserResponse

class OrderCreate(BaseModel):
    pass


class OrderItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    user: UserResponse    
    order_date: datetime
    status: str
    payment_status: str
    total_amount: Decimal
    items: Optional[List[OrderItemOut]] = []

    class Config:
        from_attributes = True


class PaginatedOrders(BaseModel):
    orders: List[OrderOut]
    total: int

class OrderStatusUpdate(BaseModel):
    status: Optional[Literal["pending", "processing", "shipped", "delivered", "cancelled"]] = None
    payment_status: Optional[Literal["unpaid", "paid", "refunded", "failed"]] = None

class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

