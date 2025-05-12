from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    title: str
    description: Optional[str]
    price: float
    stock: int 
    category_id: int

class ProductOut(ProductCreate):
    id: int
    created_at: datetime
    imageUrl: Optional[str]

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]
    stock: Optional[int]
    category_id: Optional[int]