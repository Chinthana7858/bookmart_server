from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PaginatedCategories,
)
from app.services import category_service
from app.auth.utils import require_admin

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_admin=Depends(require_admin) ):
    return category_service.create_category(db, category)

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db),current_admin=Depends(require_admin)):
    return category_service.delete_category(db, category_id)

@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    return category_service.get_all_categories(db)


@router.get("/paginated", response_model=PaginatedCategories)
def get_categories_paginated(
    skip: int = Query(0, ge=0),
    limit: int = Query(15, gt=0),
    db: Session = Depends(get_db),
):
    return category_service.get_categories_paginated(db, skip=skip, limit=limit)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    updated_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    return category_service.update_category(db, category_id, updated_data)
