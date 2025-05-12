from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart_item import CartItemCreate
from datetime import datetime

def create_cart_item(data: CartItemCreate, db: Session):
    product = db.query(Product).filter(Product.id == data.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    product.stock -= data.quantity

    cart_item = CartItem(
        user_id=data.user_id,
        product_id=data.product_id,
        quantity=data.quantity,
        added_at=datetime.utcnow()
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_cart_item(cart_item_id: int, db: Session):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if product:
        product.stock += cart_item.quantity

    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item removed and stock updated"}


def get_cart_items_by_userid(userid:int, db:Session):
      cart_items = db.query(CartItem).filter(CartItem.user_id == userid).all()
      if not cart_items:
        raise HTTPException(status_code=404, detail="No cart items found for this user.")
      return cart_items