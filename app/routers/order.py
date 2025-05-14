from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth.utils import require_admin
from app.db import get_db
from app.schemas.order import OrderCreate, OrderItemCreate, OrderOut, PaginatedOrders
from app.services.order_service import create_order, create_order_item, fetch_all_orders, fetch_all_orders_paginated
from app.services.user_service import get_orders_by_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(order, db)

@router.get("/", response_model=list[OrderOut])
def get_all_orders(db: Session = Depends(get_db),current_admin=Depends(require_admin)):
    return fetch_all_orders(db)

@router.get("/paginated", response_model=PaginatedOrders)
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(15, gt=0),
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin)
):  
    return fetch_all_orders_paginated(db, skip=skip, limit=limit)

@router.post("/items/")
def add_order_item(item: OrderItemCreate, db: Session = Depends(get_db)):
    return create_order_item(item, db)

@router.get("/user/{user_id}", response_model=list[OrderOut])
def get_orders_for_user(user_id: int, db: Session = Depends(get_db)):
    return get_orders_by_user(user_id, db)
