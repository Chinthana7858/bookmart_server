import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.product import Product
from app.models.cart_item import CartItem
from app.auth.utils import hash_password
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def create_user_and_product(db_session):
    unique_email = f"user_{uuid.uuid4().hex[:6]}@gmail.com"
    user = User(
        name="Cart User",
        email=unique_email,
        password=hash_password("password123"),
        address="123 Street",
        role="user"
    )
    db_session.add(user)
    db_session.commit()

    product = Product(
        title="Test Product",
        description="A product for testing",
        price=10.99,
        stock=20,
        imageUrl="https://via.placeholder.com/150",
        category_id=1,
        created_at=datetime.utcnow()
    )
    db_session.add(product)
    db_session.commit()

    return user, product

def test_add_to_cart(client, db_session, create_user_and_product):
    user, product = create_user_and_product
    response = client.post("/cart/", json={
        "user_id": user.id,
        "product_id": product.id,
        "quantity": 2
    })
    assert response.status_code == 200
    assert response.json()["user_id"] == user.id

def test_get_cart_items(client, db_session, create_user_and_product):
    user, product = create_user_and_product
    cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=1, added_at=datetime.utcnow())
    db_session.add(cart_item)
    db_session.commit()

    response = client.get(f"/cart/cartbyuserid/{user.id}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["product_id"] == product.id

def test_delete_cart_item(client, db_session, create_user_and_product):
    user, product = create_user_and_product
    cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=1, added_at=datetime.utcnow())
    db_session.add(cart_item)
    db_session.commit()

    response = client.delete(f"/cart/{cart_item.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Cart item removed and stock updated"
