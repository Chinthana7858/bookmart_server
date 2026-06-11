import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.cart_item import CartItem
from app.auth.utils import hash_password
from app.db import get_db

# Override database session
@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    unique_email = f"user_{uuid.uuid4().hex[:6]}@gmail.com"
    user = User(
        name="Order User",
        email=unique_email,
        password=hash_password("pass1234"),
        address="456 Test Ave",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def user_cookie(client, test_user):
    response = client.post("/auth/login", json={
        "email": test_user.email,
        "password": "pass1234"
    })
    return {"jwt": response.cookies.get("jwt")}

@pytest.fixture
def admin_user(db_session):
    admin = User(
        name="Admin User",
        email=f"admin_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("admin123"),
        address="Admin Address",
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def admin_cookie(client, admin_user):
    response = client.post("/auth/login", json={
        "email": admin_user.email,
        "password": "admin123"
    })
    return {"jwt": response.cookies.get("jwt")}

@pytest.fixture
def test_product(db_session):
    product = Product(
        title="Sample Product",
        description="For testing",
        price=50.0,
        stock=10,
        imageUrl="sample.png",
        category_id=1
    )
    db_session.add(product)
    db_session.commit()
    return product

def test_create_order(client, test_user, user_cookie):
    response = client.post("/orders/", json={}, cookies=user_cookie)
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id
    assert response.json()["status"] == "pending"
    assert response.json()["payment_status"] == "unpaid"

def test_add_order_item(client, db_session, test_user, test_product, user_cookie):
    order = Order(user_id=test_user.id)
    db_session.add(order)
    db_session.commit()
    starting_stock = test_product.stock

    payload = {
        "order_id": order.id,
        "product_id": test_product.id,
        "quantity": 1
    }
    response = client.post("/orders/items/", json=payload, cookies=user_cookie)

    db_session.refresh(test_product)
    assert response.status_code == 200
    assert response.json()["product_id"] == test_product.id
    assert test_product.stock == starting_stock - 1
    db_session.refresh(order)
    assert float(order.total_amount) == 50.0

def test_get_orders_for_user(client, db_session, test_user, user_cookie):
    # Create an order for the test user
    create_resp = client.post("/orders/", json={}, cookies=user_cookie)
    assert create_resp.status_code == 200

    # Fetch the user's orders
    get_resp = client.get("/orders/me", cookies=user_cookie)
    assert get_resp.status_code == 200
    orders = get_resp.json()
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert orders[0]["user_id"] == test_user.id

def test_get_order_by_id_for_owner(client, db_session, test_user, user_cookie):
    order = Order(user_id=test_user.id)
    db_session.add(order)
    db_session.commit()

    response = client.get(f"/orders/{order.id}", cookies=user_cookie)

    assert response.status_code == 200
    assert response.json()["id"] == order.id

def test_cannot_get_another_users_orders(client, db_session, test_user, user_cookie):
    other_user = User(
        name="Other User",
        email=f"other_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("pass1234"),
        address="Other Address",
        role="user"
    )
    db_session.add(other_user)
    db_session.commit()

    response = client.get(f"/orders/user/{other_user.id}", cookies=user_cookie)
    assert response.status_code == 403

def test_checkout_cart_creates_order_and_clears_cart(client, db_session, test_user, test_product, user_cookie):
    cart_item = CartItem(user_id=test_user.id, product_id=test_product.id, quantity=2)
    db_session.add(cart_item)
    db_session.commit()
    starting_stock = test_product.stock

    response = client.post("/orders/checkout", json={}, cookies=user_cookie)

    db_session.refresh(test_product)
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id
    assert test_product.stock == starting_stock - 2
    assert db_session.query(CartItem).filter(CartItem.user_id == test_user.id).count() == 0
    assert db_session.query(OrderItem).filter(OrderItem.order_id == response.json()["id"]).count() == 1
    assert float(response.json()["total_amount"]) == 100.0

def test_admin_can_update_order_status(client, db_session, test_user, admin_cookie):
    order = Order(user_id=test_user.id)
    db_session.add(order)
    db_session.commit()

    response = client.patch(
        f"/orders/{order.id}/status",
        json={"status": "processing", "payment_status": "paid"},
        cookies=admin_cookie
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert response.json()["payment_status"] == "paid"

def test_admin_can_search_filter_and_sort_paginated_orders(
    client,
    db_session,
    test_user,
    test_product,
    admin_cookie,
):
    matching_order = Order(
        user_id=test_user.id,
        status="processing",
        payment_status="paid",
        total_amount=150,
    )
    other_user = User(
        name="Different Buyer",
        email=f"different_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("pass1234"),
        address="Other Address",
        role="user",
    )
    db_session.add_all([matching_order, other_user])
    db_session.flush()
    db_session.add(
        OrderItem(
            order_id=matching_order.id,
            product_id=test_product.id,
            quantity=3,
        )
    )
    db_session.add(
        Order(
            user_id=other_user.id,
            status="pending",
            payment_status="unpaid",
            total_amount=25,
        )
    )
    db_session.commit()

    response = client.get(
        "/orders/paginated",
        params={
            "search": "Sample",
            "status": "processing",
            "payment_status": "paid",
            "sort_by": "total",
            "sort_order": "desc",
            "skip": 0,
            "limit": 10,
        },
        cookies=admin_cookie,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["orders"][0]["id"] == matching_order.id

def test_admin_orders_reject_invalid_sort(client, admin_cookie):
    response = client.get(
        "/orders/paginated",
        params={"sort_by": "password"},
        cookies=admin_cookie,
    )

    assert response.status_code == 422
