from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.order import OrderItemCreate, OrderStatusUpdate
from decimal import Decimal

def create_order(user_id: int, db: Session):
    new_order = Order(user_id=user_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def fetch_all_orders(db: Session):
    return db.query(Order).all()

def fetch_all_orders_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 15,
    search: str | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    sort_by: str = "order_date",
    sort_order: str = "desc",
):
    sort_columns = {
        "id": Order.id,
        "customer": User.name,
        "date": Order.order_date,
        "order_date": Order.order_date,
        "status": Order.status,
        "payment": Order.payment_status,
        "payment_status": Order.payment_status,
        "total": Order.total_amount,
        "total_amount": Order.total_amount,
    }
    if sort_by not in sort_columns:
        raise HTTPException(status_code=400, detail="Invalid order sort field")
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid order sort direction")

    query = (
        db.query(Order)
        .join(Order.user)
        .outerjoin(Order.items)
        .outerjoin(OrderItem.product)
    )

    if search:
        search_value = f"%{search.strip()}%"
        query = query.filter(
            or_(
                cast(Order.id, String).ilike(search_value),
                User.name.ilike(search_value),
                User.email.ilike(search_value),
                Product.title.ilike(search_value),
            )
        )
    if status:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)

    total = query.distinct().count()
    sort_column = sort_columns[sort_by]
    orders = (
        query.distinct()
        .order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"orders": orders, "total": total}

def get_order_by_id(order_id: int, user_id: int, user_role: str, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user_id and user_role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to view this order")
    return order

def create_order_item(data: OrderItemCreate, user_id: int, user_role: str, db: Session):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user_id and user_role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to add items to this order")

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product or product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock or product not found")

    product.stock -= data.quantity
    order.total_amount = (order.total_amount or Decimal("0")) + (product.price * data.quantity)

    order_item = OrderItem(
        order_id=data.order_id,
        product_id=data.product_id,
        quantity=data.quantity
    )
    db.add(order_item)
    db.commit()
    db.refresh(order_item)
    return order_item

def checkout_cart(user_id: int, db: Session):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    products_by_id = {
        product.id: product
        for product in db.query(Product)
        .filter(Product.id.in_([item.product_id for item in cart_items]))
        .all()
    }

    for item in cart_items:
        product = products_by_id.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.title}")

    order = Order(user_id=user_id, status="pending", payment_status="unpaid", total_amount=Decimal("0"))
    db.add(order)
    db.flush()

    for item in cart_items:
        product = products_by_id[item.product_id]
        product.stock -= item.quantity
        order.total_amount = (order.total_amount or Decimal("0")) + (product.price * item.quantity)
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity
        ))
        db.delete(item)

    db.commit()
    db.refresh(order)
    return order

def update_order_status(order_id: int, data: OrderStatusUpdate, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if data.status is not None:
        order.status = data.status
    if data.payment_status is not None:
        order.payment_status = data.payment_status
    db.commit()
    db.refresh(order)
    return order
