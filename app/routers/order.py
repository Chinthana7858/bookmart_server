from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.utils import require_admin
from app.db import get_db
from app.schemas.order import OrderCreate, OrderItemCreate, OrderOut
from app.services.order_service import create_order, create_order_item, fetch_all_orders
from app.services.user_service import get_orders_by_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(order, db)

@router.get("/", response_model=list[OrderOut])
def get_all_orders(db: Session = Depends(get_db),current_admin=Depends(require_admin)):
    return fetch_all_orders(db)

@router.post("/items/")
def add_order_item(item: OrderItemCreate, db: Session = Depends(get_db)):
    return create_order_item(item, db)

@router.get("/user/{user_id}", response_model=list[OrderOut])
def get_orders_for_user(user_id: int, db: Session = Depends(get_db)):
    return get_orders_by_user(user_id, db)