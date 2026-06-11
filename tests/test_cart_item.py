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

@pytest.fixture
def user_cookie(client, create_user_and_product):
    user, _ = create_user_and_product
    response = client.post("/auth/login", json={
        "email": user.email,
        "password": "password123"
    })
    return {"jwt": response.cookies.get("jwt")}

def test_add_to_cart(client, db_session, create_user_and_product, user_cookie):
    user, product = create_user_and_product
    starting_stock = product.stock

    response = client.post("/cart/", json={
        "product_id": product.id,
        "quantity": 2
    }, cookies=user_cookie)

    db_session.refresh(product)
    assert response.status_code == 200
    assert response.json()["user_id"] == user.id
    assert product.stock == starting_stock

def test_add_duplicate_cart_item_merges_quantity(client, db_session, create_user_and_product, user_cookie):
    user, product = create_user_and_product

    first = client.post("/cart/", json={
        "product_id": product.id,
        "quantity": 2
    }, cookies=user_cookie)
    second = client.post("/cart/", json={
        "product_id": product.id,
        "quantity": 3
    }, cookies=user_cookie)

    cart_items = db_session.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == product.id
    ).all()
    assert first.status_code == 200
    assert second.status_code == 200
    assert len(cart_items) == 1
    assert cart_items[0].quantity == 5

def test_get_cart_items(client, db_session, create_user_and_product, user_cookie):
    user, product = create_user_and_product
    cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=1, added_at=datetime.utcnow())
    db_session.add(cart_item)
    db_session.commit()

    response = client.get("/cart/me", cookies=user_cookie)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["product_id"] == product.id

def test_delete_cart_item(client, db_session, create_user_and_product, user_cookie):
    user, product = create_user_and_product
    cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=1, added_at=datetime.utcnow())
    db_session.add(cart_item)
    db_session.commit()

    response = client.delete(f"/cart/{cart_item.id}", cookies=user_cookie)
    assert response.status_code == 200
    assert response.json()["message"] == "Cart item removed successfully"

def test_update_cart_item_quantity(client, db_session, create_user_and_product, user_cookie):
    user, product = create_user_and_product
    cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=1, added_at=datetime.utcnow())
    db_session.add(cart_item)
    db_session.commit()

    response = client.put(f"/cart/{cart_item.id}", json={"quantity": 4}, cookies=user_cookie)

    db_session.refresh(cart_item)
    assert response.status_code == 200
    assert cart_item.quantity == 4

def test_cannot_view_another_users_cart(client, db_session, create_user_and_product, user_cookie):
    other_user = User(
        name="Other User",
        email=f"other_{uuid.uuid4().hex[:6]}@gmail.com",
        password=hash_password("password123"),
        address="Other Street",
        role="user"
    )
    db_session.add(other_user)
    db_session.commit()

    response = client.get(f"/cart/cartbyuserid/{other_user.id}", cookies=user_cookie)
    assert response.status_code == 403
