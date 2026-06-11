import uuid
from decimal import Decimal

import pytest

from app.auth.utils import hash_password
from app.models.order import Order
from app.models.user import User
from app.services import payment_service


@pytest.fixture
def payment_user(db_session):
    user = User(
        name="Payment User",
        email=f"payment_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("pay1234"),
        address="Payment Street",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def payment_cookie(client, payment_user):
    response = client.post("/auth/login", json={
        "email": payment_user.email,
        "password": "pay1234",
    })
    return {"jwt": response.cookies.get("jwt")}


def test_create_mock_payment_session(client, db_session, payment_user, payment_cookie, monkeypatch):
    monkeypatch.setattr(payment_service, "PAYMENT_PROVIDER", "mock")
    order = Order(user_id=payment_user.id, total_amount=Decimal("42.50"))
    db_session.add(order)
    db_session.commit()

    response = client.post(
        "/payments/checkout-session",
        json={"order_id": order.id},
        cookies=payment_cookie,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "mock"
    assert data["order_id"] == order.id
    assert float(data["amount"]) == 42.5
    assert f"/payment/{order.id}" in data["payment_url"]


def test_confirm_mock_payment_marks_order_paid(client, db_session, payment_user, payment_cookie, monkeypatch):
    monkeypatch.setattr(payment_service, "PAYMENT_PROVIDER", "mock")
    order = Order(user_id=payment_user.id, total_amount=Decimal("20.00"))
    db_session.add(order)
    db_session.commit()

    response = client.post(f"/payments/orders/{order.id}/confirm", cookies=payment_cookie)

    db_session.refresh(order)
    assert response.status_code == 200
    assert order.payment_status == "paid"
    assert order.status == "processing"


def test_user_cannot_pay_another_users_order(client, db_session, payment_cookie, monkeypatch):
    monkeypatch.setattr(payment_service, "PAYMENT_PROVIDER", "mock")
    other_user = User(
        name="Other Payment User",
        email=f"other_payment_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("pay1234"),
        address="Other Street",
        role="user",
    )
    db_session.add(other_user)
    db_session.commit()
    order = Order(user_id=other_user.id, total_amount=Decimal("20.00"))
    db_session.add(order)
    db_session.commit()

    response = client.post(
        "/payments/checkout-session",
        json={"order_id": order.id},
        cookies=payment_cookie,
    )

    assert response.status_code == 403


def test_create_stripe_payment_session(client, db_session, payment_user, payment_cookie, monkeypatch):
    order = Order(user_id=payment_user.id, total_amount=Decimal("42.50"))
    db_session.add(order)
    db_session.commit()
    created_payloads = []

    class FakeStripeSession:
        id = "cs_test_123"
        url = "https://checkout.stripe.com/c/pay/cs_test_123"

    class FakeSessionApi:
        @staticmethod
        def create(**kwargs):
            created_payloads.append(kwargs)
            return FakeStripeSession()

    class FakeCheckout:
        Session = FakeSessionApi

    class FakeStripe:
        api_key = None
        checkout = FakeCheckout

    monkeypatch.setattr(payment_service, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(payment_service, "STRIPE_SECRET_KEY", "sk_test_fake")
    monkeypatch.setattr(payment_service, "stripe", FakeStripe)

    response = client.post(
        "/payments/checkout-session",
        json={"order_id": order.id},
        cookies=payment_cookie,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "stripe"
    assert data["payment_url"] == FakeStripeSession.url
    assert data["session_id"] == FakeStripeSession.id
    assert created_payloads[0]["line_items"][0]["price_data"]["unit_amount"] == 4250
    assert created_payloads[0]["metadata"]["order_id"] == str(order.id)


def test_confirm_stripe_payment_marks_order_paid(client, db_session, payment_user, payment_cookie, monkeypatch):
    order = Order(user_id=payment_user.id, total_amount=Decimal("20.00"))
    db_session.add(order)
    db_session.commit()

    class FakeStripeSession(dict):
        def __init__(self):
            super().__init__(
                metadata={"order_id": str(order.id)},
                payment_status="paid",
            )
            self.metadata = self["metadata"]
            self.payment_status = self["payment_status"]

    class FakeSessionApi:
        @staticmethod
        def retrieve(session_id):
            assert session_id == "cs_test_paid"
            return FakeStripeSession()

    class FakeCheckout:
        Session = FakeSessionApi

    class FakeStripe:
        api_key = None
        checkout = FakeCheckout

    monkeypatch.setattr(payment_service, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(payment_service, "STRIPE_SECRET_KEY", "sk_test_fake")
    monkeypatch.setattr(payment_service, "stripe", FakeStripe)

    response = client.post(
        f"/payments/orders/{order.id}/confirm",
        json={"session_id": "cs_test_paid"},
        cookies=payment_cookie,
    )

    db_session.refresh(order)
    assert response.status_code == 200
    assert order.payment_status == "paid"
    assert order.status == "processing"
