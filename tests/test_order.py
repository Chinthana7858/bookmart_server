import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
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

def test_create_order(client, test_user):
    payload = {"user_id": test_user.id}
    response = client.post("/orders/", json=payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id

def test_add_order_item(client, db_session, test_user, test_product):
    order = Order(user_id=test_user.id)
    db_session.add(order)
    db_session.commit()

    payload = {
        "order_id": order.id,
        "product_id": test_product.id,
        "quantity": 1
    }
    response = client.post("/orders/items/", json=payload)
    assert response.status_code == 200
    assert response.json()["product_id"] == test_product.id

def test_get_orders_for_user(client, db_session, test_user):
    # Create an order for the test user
    create_resp = client.post("/orders/", json={"user_id": test_user.id})
    assert create_resp.status_code == 200

    # Fetch the user's orders
    get_resp = client.get(f"/orders/user/{test_user.id}")
    assert get_resp.status_code == 200
    orders = get_resp.json()
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert orders[0]["user_id"] == test_user.id
