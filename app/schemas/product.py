from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.category import CategoryResponse

class ProductCreate(BaseModel):
    title: str
    description: Optional[str]
    publisher: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    price: float
    stock: int 
    category_id: Optional[int] = None
    category_ids: Optional[List[int]] = None

class ProductOut(ProductCreate):
    id: int
    created_at: datetime
    imageUrl: Optional[str]
    category_id: int
    category_ids: List[int] = []
    categories: List[CategoryResponse] = []

    class Config:
        from_attributes = True


class PaginatedProducts(BaseModel):
    products: List[ProductOut]
    total: int


class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    publisher: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    price: Optional[float]
    stock: Optional[int]
    category_id: Optional[int]
    category_ids: Optional[List[int]] = None
