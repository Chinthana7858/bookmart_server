import os
import importlib
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session
try:
    import stripe
    from stripe import SignatureVerificationError
except ImportError:  # pragma: no cover - exercised only when dependency is missing at runtime
    stripe = None
    SignatureVerificationError = None

from app.models.order import Order
from app.schemas.payment import PaymentSessionCreate


PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mock").lower()
PAYMENT_CURRENCY = os.getenv("PAYMENT_CURRENCY", "USD")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
ZERO_DECIMAL_CURRENCIES = {
    "BIF",
    "CLP",
    "DJF",
    "GNF",
    "JPY",
    "KMF",
    "KRW",
    "MGA",
    "PYG",
    "RWF",
    "UGX",
    "VND",
    "VUV",
    "XAF",
    "XOF",
    "XPF",
}


def _get_user_order(order_id: int, user_id: int, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to pay this order")
    return order


def _validate_payable_order(order: Order):
    amount = Decimal(order.total_amount or 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Order amount must be greater than zero")
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order is already paid")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot pay a cancelled order")
    return amount


def _active_provider():
    return "stripe" if PAYMENT_PROVIDER in {"stripe", "real"} else PAYMENT_PROVIDER


def _stripe_client():
    global stripe, SignatureVerificationError
    if stripe is None:
        try:
            stripe = importlib.import_module("stripe")
            SignatureVerificationError = getattr(stripe, "SignatureVerificationError")
        except ImportError as exc:
            raise HTTPException(status_code=500, detail="Stripe dependency is not installed") from exc
    if stripe is None:
        raise HTTPException(status_code=500, detail="Stripe dependency is not installed")
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY is not configured")
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


def _to_stripe_amount(amount: Decimal, currency: str):
    normalized_currency = currency.upper()
    if normalized_currency in ZERO_DECIMAL_CURRENCIES:
        return int(amount.quantize(Decimal("1")))
    return int((amount * Decimal("100")).quantize(Decimal("1")))


def _mark_order_paid(order: Order, db: Session):
    if order.payment_status != "paid":
        order.payment_status = "paid"
        order.status = "processing"
        db.commit()
        db.refresh(order)
    return order


def create_payment_session(data: PaymentSessionCreate, user_id: int, db: Session):
    order = _get_user_order(data.order_id, user_id, db)
    amount = _validate_payable_order(order)
    provider = _active_provider()

    if provider == "stripe":
        stripe_client = _stripe_client()
        try:
            session = stripe_client.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                customer_email=getattr(order.user, "email", None),
                line_items=[
                    {
                        "price_data": {
                            "currency": PAYMENT_CURRENCY.lower(),
                            "product_data": {
                                "name": f"BookMart Order #{order.id}",
                            },
                            "unit_amount": _to_stripe_amount(amount, PAYMENT_CURRENCY),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(user_id),
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order.id),
                        "user_id": str(user_id),
                    }
                },
                success_url=f"{FRONTEND_BASE_URL}/payment/{order.id}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{FRONTEND_BASE_URL}/payment/{order.id}?payment=cancelled",
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Stripe checkout session failed: {exc}") from exc

        return {
            "provider": provider,
            "order_id": order.id,
            "amount": amount,
            "currency": PAYMENT_CURRENCY,
            "payment_url": session.url,
            "session_id": session.id,
        }

    if provider != "mock":
        raise HTTPException(status_code=501, detail=f"Unsupported payment provider: {PAYMENT_PROVIDER}")

    session_id = f"mock_order_{order.id}"
    return {
        "provider": provider,
        "order_id": order.id,
        "amount": amount,
        "currency": PAYMENT_CURRENCY,
        "payment_url": f"{FRONTEND_BASE_URL}/payment/{order.id}?session_id={session_id}",
        "session_id": session_id,
    }


def confirm_mock_payment(order_id: int, user_id: int, db: Session):
    order = _get_user_order(order_id, user_id, db)

    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot pay a cancelled order")
    _mark_order_paid(order, db)

    return {
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "message": "Payment confirmed",
    }


def confirm_payment(order_id: int, user_id: int, db: Session, session_id: str | None = None):
    provider = _active_provider()
    if provider == "mock":
        return confirm_mock_payment(order_id, user_id, db)

    if provider != "stripe":
        raise HTTPException(status_code=501, detail=f"Unsupported payment provider: {PAYMENT_PROVIDER}")
    if not session_id:
        raise HTTPException(status_code=400, detail="Stripe session_id is required")

    order = _get_user_order(order_id, user_id, db)
    stripe_client = _stripe_client()
    try:
        session = stripe_client.checkout.Session.retrieve(session_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Stripe checkout lookup failed: {exc}") from exc

    if str(session.metadata.get("order_id")) != str(order.id):
        raise HTTPException(status_code=400, detail="Stripe session does not match this order")
    if session.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Stripe payment is not complete")

    _mark_order_paid(order, db)
    return {
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "message": "Payment confirmed",
    }


def handle_stripe_webhook(payload: bytes, signature: str | None, db: Session):
    stripe_client = _stripe_client()
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET is not configured")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = stripe_client.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook payload") from exc
    except SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature") from exc

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        if order_id and session.get("payment_status") == "paid":
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                _mark_order_paid(order, db)

    return {"received": True}
