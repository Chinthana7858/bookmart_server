from pydantic import BaseModel
from datetime import datetime

from app.schemas.product import ProductOut

class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartItemOut(CartItemCreate):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True
        
class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    added_at: datetime
    product: ProductOut 

    class Config:
        from_attributes = True