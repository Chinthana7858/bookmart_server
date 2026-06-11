from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_all_categories(db: Session):
    return db.query(Category).all()


def get_categories_paginated(db: Session, skip: int = 0, limit: int = 15):
    categories = db.query(Category).order_by(Category.id.desc()).offset(skip).limit(limit).all()
    total = db.query(Category).count()
    return {"categories": categories, "total": total}


def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

def update_category(db: Session, category_id: int, updated_data: CategoryUpdate):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if updated_data.name is not None:
        category.name = updated_data.name
    if updated_data.description is not None:
        category.description = updated_data.description

    db.commit()
    db.refresh(category)
    return category
