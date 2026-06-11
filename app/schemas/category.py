from pydantic import BaseModel
from typing import List

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


class PaginatedCategories(BaseModel):
    categories: List[CategoryResponse]
    total: int
