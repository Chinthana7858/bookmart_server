from decimal import Decimal
from pydantic import BaseModel


class PaymentSessionCreate(BaseModel):
    order_id: int


class PaymentConfirmCreate(BaseModel):
    session_id: str | None = None


class PaymentSessionOut(BaseModel):
    provider: str
    order_id: int
    amount: Decimal
    currency: str
    payment_url: str
    session_id: str


class PaymentConfirmOut(BaseModel):
    order_id: int
    status: str
    payment_status: str
    message: str
