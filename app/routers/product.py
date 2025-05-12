import json
import cloudinary
from fastapi import APIRouter, Depends, HTTPException, File, Query, UploadFile, Form
from sqlalchemy.orm import Session
from app.auth.utils import require_admin
from app.db import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services import product_service
from app.models.product import Product
from app.services.product_service import create_product


router = APIRouter()

@router.post("/", response_model=ProductOut)
def upload_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),  
    category_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return create_product(title, description, price, category_id, stock, file, db)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return product_service.delete_product(product_id, db)

@router.get("/getproductbyid/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product_by_id(product_id, db)

@router.get("/getbycategoryid/{category_id}", response_model=list[ProductOut])
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    return product_service.get_products_by_category(category_id, db)

@router.get("/search", response_model=list[ProductOut])
def search_products(name: str = Query(...), db: Session = Depends(get_db),):
    return product_service.search_products_by_name(name, db)

@router.get("/paginated")
def get_paginated_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    products = db.query(Product).offset(offset).limit(limit).all()
    total = db.query(Product).count()
    return {"products": products, "total": total}

@router.get("/sorted", response_model=list[ProductOut])
def get_sorted_products(
    sort_by: str = Query(..., description="Field to sort by: price, stock, or created_at"),
    order: str = Query(..., description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
):
    return product_service.get_sorted_products(sort_by, order, db)



# @router.put("/{product_id}", response_model=ProductOut)
# def update_product(
#     product_id: int,
#     title: str = Form(None),
#     description: str = Form(None),
#     price: float = Form(None),
#     stock: int = Form(None),
#     category_id: int = Form(None),
#     file: UploadFile = File(None),
#     db: Session = Depends(get_db),
#     current_admin=Depends(require_admin)
# ):
#     return product_service.update_product(
#         product_id, title, description, price, stock, category_id, file, db
#     )

# @router.get("/", response_model=list[ProductOut])
# def get_all_products(db: Session = Depends(get_db)):
#     return product_service.get_all_products(db)