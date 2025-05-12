import uuid
import pytest
from app.models.user import User
from app.auth.utils import hash_password
from fastapi.testclient import TestClient

from app.routers import user

@pytest.fixture
def create_test_user(db_session):
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


def test_list_users(client, create_test_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user(client, create_test_user):
    response = client.get(f"/users/{create_test_user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == create_test_user.email

def test_update_user_info(client, create_test_user):
    response = client.put(
        f"/users/{create_test_user.id}",
        json={"name": "Updated Name", "address": "New Address"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

def test_update_password_success(client, create_test_user):
    response = client.put(
        f"/users/{create_test_user.id}/password",
        json={"current_password": "admin123", "new_password": "newpass456"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

def test_update_password_failure(client, create_test_user):
    response = client.put(
        f"/users/{create_test_user.id}/password",
        json={"current_password": "wrongpass", "new_password": "newpass456"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect current password"
