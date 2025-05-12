import uuid
import pytest
from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.auth.utils import hash_password
from app.models.user import User

@pytest.fixture
def create_admin_user(db_session):
    unique_email = f"admin_{uuid.uuid4().hex[:6]}@gmail.com"
    admin = User(
        name="Admin",
        email=unique_email,
        password=hash_password("admin123"),
        address="Admin Street",
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def admin_token(client, create_admin_user):
    response = client.post("/auth/login", json={
        "email": create_admin_user.email,
        "password": "admin123"
    })
    return response.cookies.get("jwt")

def test_create_category(client, db_session, admin_token):
    response = client.post(
        "/categories/",
        json={"name": "Tech", "description": "Technology related books"},
        cookies={"jwt": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tech"
    assert "id" in data

def test_delete_category(client, db_session, admin_token):
    # Create a category to delete
    category = Category(name="Temp Category", description="To delete")
    db_session.add(category)
    db_session.commit()

    response = client.delete(
        f"/categories/{category.id}",
        cookies={"jwt": admin_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"

def test_get_all_categories(client):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
