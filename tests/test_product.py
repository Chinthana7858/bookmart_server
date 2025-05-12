import io
import uuid
import pytest
from app.models.product import Product
from app.models.category import Category
from app.auth.utils import hash_password
from app.models.user import User


@pytest.fixture
def create_admin_and_category(db_session):
    admin_email = f"admin_{uuid.uuid4().hex}@gmail.com"
    admin = User(
        name="Admin",
        email=admin_email,
        password=hash_password("admin123"),
        address="Admin Street",
        role="admin"
    )
    db_session.add(admin)

    # Create category
    category = Category(name="TestCat", description="desc")
    db_session.add(category)
    db_session.commit()
    return admin, category


@pytest.fixture
def admin_token(client, create_admin_and_category):
    admin, _ = create_admin_and_category
    response = client.post("/auth/login", json={
        "email": admin.email,
        "password": "admin123"
    })
    return response.cookies.get("jwt")


def test_create_product_with_local_image(client, db_session, create_admin_and_category, admin_token):
    _, category = create_admin_and_category

    with open("tests/assets/39016.jpg", "rb") as file:  
        response = client.post(
            "/products/",
            data={
                "title": "Local Image Product",
                "description": "This product uses local image",
                "price": 25.50,
                "stock": 10,
                "category_id": category.id
            },
            files={"file": ("sample.jpg", file, "image/jpeg")},
            cookies={"jwt": admin_token}
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Local Image Product"


def test_get_product_by_id(client, db_session):
    product = db_session.query(Product).first()
    if not product:
        pytest.skip("No product available to test retrieval.")
    response = client.get(f"/products/getproductbyid/{product.id}")
    assert response.status_code == 200
    assert response.json()["id"] == product.id


def test_get_products_by_category(client, db_session):
    product = db_session.query(Product).first()
    if not product:
        pytest.skip("No product for category test.")
    response = client.get(f"/products/getbycategoryid/{product.category_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_products(client):
    response = client.get("/products/search?name=Sample")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_paginated_products(client):
    response = client.get("/products/paginated?limit=5&offset=0")
    assert response.status_code == 200
    assert "products" in response.json()
    assert "total" in response.json()


def test_get_sorted_products(client):
    response = client.get("/products/sorted?sort_by=price&order=asc")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_product(client, db_session, admin_token):
    product = db_session.query(Product).first()
    if not product:
        pytest.skip("No product to delete")
    response = client.delete(f"/products/{product.id}", cookies={"jwt": admin_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"
