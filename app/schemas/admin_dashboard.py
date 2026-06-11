from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class DashboardMetric(BaseModel):
    label: str
    value: Decimal | int
    helper: str | None = None


class DashboardBreakdownItem(BaseModel):
    key: str
    label: str
    count: int


class DashboardRecentOrder(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    order_date: datetime
    status: str
    payment_status: str
    total_amount: Decimal
    item_count: int


class DashboardProductSummary(BaseModel):
    id: int
    title: str
    stock: int
    price: Decimal
    imageUrl: str | None = None
    author: str | None = None
    sold_quantity: int | None = None
    revenue: Decimal | None = None


class DashboardCategorySummary(BaseModel):
    id: int
    name: str
    product_count: int
    sold_quantity: int


class AdminDashboardSummary(BaseModel):
    total_revenue: Decimal
    revenue_today: Decimal
    revenue_this_month: Decimal
    total_orders: int
    total_books: int
    total_customers: int
    total_admins: int
    average_order_value: Decimal
    paid_orders: int
    unpaid_orders: int
    pending_orders: int
    low_stock_count: int
    out_of_stock_count: int
    unpaid_amount: Decimal
    order_status_breakdown: List[DashboardBreakdownItem]
    payment_status_breakdown: List[DashboardBreakdownItem]
    recent_orders: List[DashboardRecentOrder]
    unpaid_recent_orders: List[DashboardRecentOrder]
    low_stock_books: List[DashboardProductSummary]
    top_selling_books: List[DashboardProductSummary]
    top_categories: List[DashboardCategorySummary]
