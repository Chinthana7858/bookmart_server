from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.cart_item import CartItemCreate, CartItemOut
from app.services.cart_item_service import create_cart_item, get_cart_items_by_userid, remove_cart_item

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=CartItemOut)
def add_to_cart(data: CartItemCreate, db: Session = Depends(get_db)):
    return create_cart_item(data, db)

@router.delete("/{cart_item_id}")
def delete_from_cart(cart_item_id: int, db: Session = Depends(get_db)):
    return remove_cart_item(cart_item_id, db)

@router.get("/cartbyuserid/{user_id}", response_model=list[CartItemOut])
def read_cart_items(user_id: int, db: Session = Depends(get_db)):
    return get_cart_items_by_userid(user_id, db)