from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth.utils import require_admin, require_user
from app.db import get_db
from app.schemas.order import OrderCreate, OrderItemCreate, OrderOut, OrderStatusUpdate, PaginatedOrders
from app.services.order_service import checkout_cart, create_order, create_order_item, fetch_all_orders, fetch_all_orders_paginated, get_order_by_id, update_order_status
from app.services.user_service import get_orders_by_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderOut, include_in_schema=False)
@router.post("/", response_model=OrderOut)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    return create_order(current_user.id, db)

@router.get("/", response_model=list[OrderOut])
def get_all_orders(db: Session = Depends(get_db),current_admin=Depends(require_admin)):
    return fetch_all_orders(db)

@router.get("/paginated", response_model=PaginatedOrders)
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(15, gt=0),
    search: str | None = Query(None),
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"] | None = Query(None),
    payment_status: Literal["unpaid", "paid", "refunded", "failed"] | None = Query(None),
    sort_by: Literal[
        "id",
        "customer",
        "date",
        "order_date",
        "status",
        "payment",
        "payment_status",
        "total",
        "total_amount",
    ] = Query("order_date"),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin)
):  
    return fetch_all_orders_paginated(
        db,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        payment_status=payment_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )

@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return update_order_status(order_id, data, db)

@router.post("/items", include_in_schema=False)
@router.post("/items/")
def add_order_item(item: OrderItemCreate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    return create_order_item(item, current_user.id, current_user.role, db)

@router.post("/checkout", response_model=OrderOut)
def checkout_my_cart(db: Session = Depends(get_db), current_user=Depends(require_user)):
    return checkout_cart(current_user.id, db)

@router.get("/me", response_model=list[OrderOut])
def get_my_orders(db: Session = Depends(get_db), current_user=Depends(require_user)):
    return get_orders_by_user(current_user.id, db)

@router.get("/user/{user_id}", response_model=list[OrderOut])
def get_orders_for_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_user)):
    if user_id != current_user.id and current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not allowed to view these orders")
    return get_orders_by_user(user_id, db)

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return get_order_by_id(order_id, current_user.id, current_user.role, db)
