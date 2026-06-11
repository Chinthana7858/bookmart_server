from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.auth.utils import require_user
from app.db import get_db
from app.schemas.payment import PaymentConfirmCreate, PaymentConfirmOut, PaymentSessionCreate, PaymentSessionOut
from app.services.payment_service import confirm_payment as confirm_order_payment
from app.services.payment_service import create_payment_session, handle_stripe_webhook

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout-session", response_model=PaymentSessionOut)
def checkout_session(
    data: PaymentSessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return create_payment_session(data, current_user.id, db)


@router.post("/orders/{order_id}/confirm", response_model=PaymentConfirmOut)
def confirm_payment(
    order_id: int,
    data: PaymentConfirmCreate | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return confirm_order_payment(
        order_id,
        current_user.id,
        db,
        session_id=data.session_id if data else None,
    )


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    return handle_stripe_webhook(payload, stripe_signature, db)
