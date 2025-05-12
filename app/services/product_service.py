from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from cloudinary.uploader import upload
from app.cloudinary_config import *
from fastapi import HTTPException

def create_product(title, description, price, category_id, stock, file, db: Session):
    upload_result = upload(file.file, folder="bookmart")
    image_url = upload_result.get("secure_url")

    new_product = Product(
        title=title,
        description=description,
        price=price,
        category_id=category_id,
        stock=stock,
        imageUrl=image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_product_by_id(product_id: int, db: Session):
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
         raise HTTPException(status_code=404, detail="Product not found")
    return product

def get_products_by_category(category_id: int, db: Session):
    return db.query(Product).filter(Product.category_id == category_id).all()

def delete_product(product_id: int, db: Session):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

def search_products_by_name(name: str, db: Session):
    return db.query(Product).filter(Product.title.ilike(f"%{name}%")).all()

def get_all_products_paginated(db: Session, limit: int, offset: int):
    return db.query(Product).offset(offset).limit(limit).all()

def get_sorted_products(sort_by: str, order: str, db: Session):
    if sort_by not in {"price", "stock", "created_at"}:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid sort order")

    column = getattr(Product, sort_by)
    query = db.query(Product).order_by(column.asc() if order == "asc" else column.desc())
    return query.all()



# def update_product(product_id, title, description, price, stock, category_id, file, db):
#     product = db.query(Product).get(product_id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     # Upload new image if provided
#     if file:
#         upload_result = upload(file.file, folder="bookmart")
#         product.imageUrl = upload_result.get("secure_url")

#     if title is not None:
#         product.title = title
#     if description is not None:
#         product.description = description
#     if price is not None:
#         product.price = price
#     if stock is not None:
#         product.stock = stock
#     if category_id is not None:
#         product.category_id = category_id

#     db.commit()
#     db.refresh(product)
#     return product


# def get_all_products(db: Session):
#     return db.query(Product).all()