from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart_item import CartItemCreate, CartItemUpdate
from datetime import datetime

def create_cart_item(data: CartItemCreate, user_id: int, db: Session):
    if data.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    product = db.query(Product).filter(Product.id == data.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == data.product_id)
        .first()
    )
    requested_quantity = data.quantity + (existing_item.quantity if existing_item else 0)

    if product.stock < requested_quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    if existing_item:
        existing_item.quantity = requested_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    cart_item = CartItem(
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity,
        added_at=datetime.utcnow()
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

def update_cart_item(cart_item_id: int, data: CartItemUpdate, user_id: int, user_role: str, db: Session):
    if data.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if cart_item.user_id != user_id and user_role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to update this cart item")

    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart_item.quantity = data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_cart_item(cart_item_id: int, user_id: int, user_role: str, db: Session):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if cart_item.user_id != user_id and user_role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to remove this cart item")

    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item removed successfully"}


def get_cart_items_by_userid(userid:int, db:Session):
      cart_items = db.query(CartItem).filter(CartItem.user_id == userid).all()
      return cart_items
