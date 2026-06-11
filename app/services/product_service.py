from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate
from cloudinary.uploader import upload
from app.cloudinary_config import *
from fastapi import HTTPException

def _get_categories(db: Session, category_ids: list[int]):
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    if len(categories) != len(set(category_ids)):
        raise HTTPException(status_code=400, detail="One or more categories were not found")
    return categories

def _normalize_category_ids(category_id: int | None, category_ids: list[int] | None):
    normalized = [int(category_id)] if category_id is not None else []
    if category_ids:
        normalized.extend(int(cat_id) for cat_id in category_ids)
    deduped = list(dict.fromkeys(normalized))
    if not deduped:
        raise HTTPException(status_code=400, detail="At least one category is required")
    return deduped

def create_product(
    title,
    description,
    price,
    category_id,
    category_ids,
    stock,
    file,
    db: Session,
    publisher=None,
    author=None,
    language=None,
):
    upload_result = upload(file.file, folder="bookmart")
    image_url = upload_result.get("secure_url")
    normalized_category_ids = _normalize_category_ids(category_id, category_ids)
    categories = _get_categories(db, normalized_category_ids)

    new_product = Product(
        title=title,
        description=description,
        publisher=publisher,
        author=author,
        language=language,
        price=price,
        category_id=normalized_category_ids[0],
        stock=stock,
        imageUrl=image_url
    )
    new_product.categories = categories
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_product_by_id(product_id: int, db: Session):
    product=(
        db.query(Product)
        .options(selectinload(Product.categories))
        .filter(Product.id==product_id)
        .first()
    )
    if not product:
         raise HTTPException(status_code=404, detail="Product not found")
    return product

def get_products_by_category(category_id: int, db: Session):
    return (
        db.query(Product)
        .options(selectinload(Product.categories))
        .outerjoin(Product.categories)
        .filter(or_(Category.id == category_id, Product.category_id == category_id))
        .distinct()
        .all()
    )

def delete_product(product_id: int, db: Session):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

def search_products_by_name(name: str, db: Session):
    return (
        db.query(Product)
        .options(selectinload(Product.categories))
        .filter(Product.title.ilike(f"%{name}%"))
        .all()
    )

def get_all_products_paginated(db: Session, limit: int, offset: int):
    products = (
        db.query(Product)
        .options(selectinload(Product.categories))
        .order_by(func.random())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Product).count()
    return {"products": products, "total": total}

def get_sorted_products(sort_by: str, order: str, db: Session):
    if sort_by not in {"price", "stock", "created_at"}:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid sort order")

    column = getattr(Product, sort_by)
    query = (
        db.query(Product)
        .options(selectinload(Product.categories))
        .order_by(column.asc() if order == "asc" else column.desc())
    )
    return query.all()

def update_product(
    product_id,
    title,
    description,
    price,
    stock,
    category_id,
    category_ids,
    file,
    db,
    publisher=None,
    author=None,
    language=None,
):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if file:
        upload_result = upload(file.file, folder="bookmart")
        product.imageUrl = upload_result.get("secure_url")

    if title is not None:
        product.title = title
    if description is not None:
        product.description = description
    if publisher is not None:
        product.publisher = publisher
    if author is not None:
        product.author = author
    if language is not None:
        product.language = language
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if category_id is not None or category_ids is not None:
        normalized_category_ids = _normalize_category_ids(category_id, category_ids)
        product.category_id = normalized_category_ids[0]
        product.categories = _get_categories(db, normalized_category_ids)

    db.commit()
    db.refresh(product)
    return product


# def get_all_products(db: Session):
#     return db.query(Product).all()
