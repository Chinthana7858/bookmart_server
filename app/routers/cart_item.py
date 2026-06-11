from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.utils import require_user
from app.db import get_db
from app.schemas.cart_item import CartItemCreate, CartItemOut, CartItemUpdate
from app.services.cart_item_service import create_cart_item, get_cart_items_by_userid, remove_cart_item, update_cart_item

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("", response_model=CartItemOut, include_in_schema=False)
@router.post("/", response_model=CartItemOut)
def add_to_cart(data: CartItemCreate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    return create_cart_item(data, current_user.id, db)

@router.delete("/{cart_item_id}")
def delete_from_cart(cart_item_id: int, db: Session = Depends(get_db), current_user=Depends(require_user)):
    return remove_cart_item(cart_item_id, current_user.id, current_user.role, db)

@router.put("/{cart_item_id}", response_model=CartItemOut)
def update_cart(cart_item_id: int, data: CartItemUpdate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    return update_cart_item(cart_item_id, data, current_user.id, current_user.role, db)

@router.get("/me", response_model=list[CartItemOut])
def read_my_cart_items(db: Session = Depends(get_db), current_user=Depends(require_user)):
    return get_cart_items_by_userid(current_user.id, db)

@router.get("/cartbyuserid/{user_id}", response_model=list[CartItemOut])
def read_cart_items(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_user)):
    if user_id != current_user.id and current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not allowed to view this cart")
    return get_cart_items_by_userid(user_id, db)
