from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderItemCreate

def create_order(data: OrderCreate, db: Session):
    new_order = Order(user_id=data.user_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def fetch_all_orders(db: Session):
    return db.query(Order).all()

def fetch_all_orders_paginated(db: Session, skip: int = 0, limit: int = 15):
    orders = db.query(Order).order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
    total = db.query(Order).count()
    return {"orders": orders, "total": total}

def create_order_item(data: OrderItemCreate, db: Session):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product or product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock or product not found")

    product.stock -= data.quantity

    order_item = OrderItem(
        order_id=data.order_id,
        product_id=data.product_id,
        quantity=data.quantity
    )
    db.add(order_item)
    db.commit()
    db.refresh(order_item)
    return order_item
