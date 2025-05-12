from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.category import Category
from app.schemas.category import CategoryCreate

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_all_categories(db: Session):
    return db.query(Category).all()


def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# def update_category(db: Session, category_id: int, updated_data: CategoryCreate):
#     category = db.query(Category).filter(Category.id == category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")

#     category.name = updated_data.name
#     category.description = updated_data.description
#     db.commit()
#     db.refresh(category)
#     return category
