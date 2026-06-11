from pydantic import BaseModel
from datetime import datetime

from app.schemas.product import ProductOut

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    added_at: datetime
    product: ProductOut 

    class Config:
        from_attributes = True
