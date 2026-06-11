from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.product import Product, product_categories
from app.models.user import User
from app.schemas.admin_dashboard import (
    AdminDashboardSummary,
    DashboardBreakdownItem,
    DashboardCategorySummary,
    DashboardProductSummary,
    DashboardRecentOrder,
)

ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
PAYMENT_STATUSES = ["unpaid", "paid", "refunded", "failed"]
LOW_STOCK_THRESHOLD = 10


def _decimal(value) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))


def _count(value) -> int:
    return int(value or 0)


def _title(value: str) -> str:
    return value.replace("_", " ").title()


def _order_to_summary(order: Order) -> DashboardRecentOrder:
    return DashboardRecentOrder(
        id=order.id,
        customer_name=order.user.name if order.user else "Unknown customer",
        customer_email=order.user.email if order.user else "No email",
        order_date=order.order_date,
        status=order.status,
        payment_status=order.payment_status,
        total_amount=_decimal(order.total_amount),
        item_count=sum(item.quantity for item in order.items),
    )


def _get_breakdown(db: Session, column, keys: list[str]) -> list[DashboardBreakdownItem]:
    rows = db.query(column, func.count(Order.id)).group_by(column).all()
    counts = {key: _count(count) for key, count in rows}

    return [
        DashboardBreakdownItem(
            key=key,
            label=_title(key),
            count=counts.get(key, 0),
        )
        for key in keys
    ]


def _get_top_categories(db: Session) -> list[DashboardCategorySummary]:
    product_counts = dict(
        db.query(
            product_categories.c.category_id,
            func.count(product_categories.c.product_id),
        )
        .group_by(product_categories.c.category_id)
        .all()
    )

    rows = (
        db.query(
            Category.id,
            Category.name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_quantity"),
        )
        .outerjoin(product_categories, Category.id == product_categories.c.category_id)
        .outerjoin(Product, Product.id == product_categories.c.product_id)
        .outerjoin(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Category.id, Category.name)
        .order_by(func.coalesce(func.sum(OrderItem.quantity), 0).desc(), Category.name.asc())
        .limit(5)
        .all()
    )

    return [
        DashboardCategorySummary(
            id=row.id,
            name=row.name,
            product_count=_count(product_counts.get(row.id)),
            sold_quantity=_count(row.sold_quantity),
        )
        for row in rows
    ]


def get_admin_dashboard_summary(db: Session) -> AdminDashboardSummary:
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), time.min)
    month_start = datetime(now.year, now.month, 1)

    paid_order_query = db.query(Order).filter(Order.payment_status == "paid")

    total_revenue = _decimal(paid_order_query.with_entities(func.sum(Order.total_amount)).scalar())
    revenue_today = _decimal(
        paid_order_query.filter(Order.order_date >= today_start)
        .with_entities(func.sum(Order.total_amount))
        .scalar()
    )
    revenue_this_month = _decimal(
        paid_order_query.filter(Order.order_date >= month_start)
        .with_entities(func.sum(Order.total_amount))
        .scalar()
    )

    total_orders = _count(db.query(func.count(Order.id)).scalar())
    total_books = _count(db.query(func.count(Product.id)).scalar())
    total_customers = _count(
        db.query(func.count(User.id)).filter(func.lower(User.role) == "user").scalar()
    )
    total_admins = _count(
        db.query(func.count(User.id)).filter(func.lower(User.role) == "admin").scalar()
    )
    paid_orders = _count(db.query(func.count(Order.id)).filter(Order.payment_status == "paid").scalar())
    unpaid_orders = _count(
        db.query(func.count(Order.id)).filter(Order.payment_status == "unpaid").scalar()
    )
    pending_orders = _count(db.query(func.count(Order.id)).filter(Order.status == "pending").scalar())
    low_stock_count = _count(
        db.query(func.count(Product.id))
        .filter(Product.stock > 0, Product.stock <= LOW_STOCK_THRESHOLD)
        .scalar()
    )
    out_of_stock_count = _count(db.query(func.count(Product.id)).filter(Product.stock <= 0).scalar())
    unpaid_amount = _decimal(
        db.query(func.sum(Order.total_amount)).filter(Order.payment_status == "unpaid").scalar()
    )
    average_order_value = (
        (total_revenue / Decimal(paid_orders)).quantize(Decimal("0.01"))
        if paid_orders
        else Decimal("0.00")
    )

    recent_orders = (
        db.query(Order)
        .join(Order.user)
        .outerjoin(Order.items)
        .order_by(Order.order_date.desc(), Order.id.desc())
        .limit(5)
        .all()
    )

    unpaid_recent_orders = (
        db.query(Order)
        .join(Order.user)
        .outerjoin(Order.items)
        .filter(Order.payment_status == "unpaid")
        .order_by(Order.order_date.desc(), Order.id.desc())
        .limit(5)
        .all()
    )

    low_stock_books = (
        db.query(Product)
        .filter(Product.stock <= LOW_STOCK_THRESHOLD)
        .order_by(Product.stock.asc(), Product.title.asc())
        .limit(6)
        .all()
    )

    top_selling_rows = (
        db.query(
            Product.id,
            Product.title,
            Product.stock,
            Product.price,
            Product.imageUrl,
            Product.author,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_quantity"),
            func.coalesce(func.sum(OrderItem.quantity * Product.price), 0).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id, Product.title, Product.stock, Product.price, Product.imageUrl, Product.author)
        .order_by(func.coalesce(func.sum(OrderItem.quantity), 0).desc(), Product.title.asc())
        .limit(5)
        .all()
    )

    return AdminDashboardSummary(
        total_revenue=total_revenue,
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        total_orders=total_orders,
        total_books=total_books,
        total_customers=total_customers,
        total_admins=total_admins,
        average_order_value=average_order_value,
        paid_orders=paid_orders,
        unpaid_orders=unpaid_orders,
        pending_orders=pending_orders,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        unpaid_amount=unpaid_amount,
        order_status_breakdown=_get_breakdown(db, Order.status, ORDER_STATUSES),
        payment_status_breakdown=_get_breakdown(db, Order.payment_status, PAYMENT_STATUSES),
        recent_orders=[_order_to_summary(order) for order in recent_orders],
        unpaid_recent_orders=[_order_to_summary(order) for order in unpaid_recent_orders],
        low_stock_books=[
            DashboardProductSummary(
                id=product.id,
                title=product.title,
                stock=product.stock,
                price=_decimal(product.price),
                imageUrl=product.imageUrl,
                author=product.author,
            )
            for product in low_stock_books
        ],
        top_selling_books=[
            DashboardProductSummary(
                id=row.id,
                title=row.title,
                stock=row.stock,
                price=_decimal(row.price),
                imageUrl=row.imageUrl,
                author=row.author,
                sold_quantity=_count(row.sold_quantity),
                revenue=_decimal(row.revenue),
            )
            for row in top_selling_rows
        ],
        top_categories=_get_top_categories(db),
    )
