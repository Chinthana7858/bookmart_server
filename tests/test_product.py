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
    second_category = Category(name="SecondCat", description="another")
    db_session.add(second_category)
    db_session.commit()

    with open("tests/assets/39016.jpg", "rb") as file:  
        response = client.post(
            "/products/",
            data={
                "title": "Local Image Product",
                "description": "This product uses local image",
                "publisher": "BookMart Press",
                "author": "Ada Writer",
                "language": "English",
                "price": 25.50,
                "stock": 10,
                "category_ids": f"[{category.id},{second_category.id}]",
            },
            files={"file": ("sample.jpg", file, "image/jpeg")},
            cookies={"jwt": admin_token}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Local Image Product"
    assert data["publisher"] == "BookMart Press"
    assert data["author"] == "Ada Writer"
    assert data["language"] == "English"
    assert set(data["category_ids"]) == {category.id, second_category.id}
    assert len(data["categories"]) == 2


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
    category_id = product.category_ids[0] if product.category_ids else product.category_id
    response = client.get(f"/products/getbycategoryid/{category_id}")
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


def test_update_product_details(client, db_session, create_admin_and_category, admin_token):
    _, category = create_admin_and_category
    second_category = Category(name="UpdatedCat", description="second")
    db_session.add(second_category)
    db_session.commit()
    product = Product(
        title="Original Product",
        description="Original description",
        publisher="Original Press",
        author="Original Author",
        language="English",
        price=10.00,
        stock=4,
        category_id=category.id,
        imageUrl="https://example.com/original.jpg",
    )
    product.categories = [category]
    db_session.add(product)
    db_session.commit()

    response = client.put(
        f"/products/{product.id}",
        data={
            "title": "Updated Product",
            "description": "Updated description",
            "publisher": "Updated Press",
            "author": "Updated Author",
            "language": "Sinhala",
            "price": 15.75,
            "stock": 8,
            "category_ids": f"[{category.id},{second_category.id}]",
        },
        cookies={"jwt": admin_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Product"
    assert data["description"] == "Updated description"
    assert data["publisher"] == "Updated Press"
    assert data["author"] == "Updated Author"
    assert data["language"] == "Sinhala"
    assert float(data["price"]) == 15.75
    assert data["stock"] == 8
    assert set(data["category_ids"]) == {category.id, second_category.id}


def test_delete_product(client, db_session, admin_token):
    product = db_session.query(Product).first()
    if not product:
        pytest.skip("No product to delete")
    response = client.delete(f"/products/{product.id}", cookies={"jwt": admin_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"
