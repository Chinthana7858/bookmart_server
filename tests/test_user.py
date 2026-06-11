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

@pytest.fixture
def admin_cookie(client, create_test_user):
    response = client.post("/auth/login", json={
        "email": create_test_user.email,
        "password": "admin123",
    })
    return {"jwt": response.cookies.get("jwt")}


def test_list_users(client, create_test_user, admin_cookie):
    response = client.get("/users/", cookies=admin_cookie)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_paginated(client, create_test_user, admin_cookie):
    response = client.get("/users/paginated?skip=0&limit=10", cookies=admin_cookie)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["users"], list)
    assert data["total"] >= 1

def test_get_user(client, create_test_user, admin_cookie):
    response = client.get(f"/users/{create_test_user.id}", cookies=admin_cookie)
    assert response.status_code == 200
    assert response.json()["email"] == create_test_user.email

def test_update_user_info(client, create_test_user, admin_cookie):
    response = client.put(
        f"/users/{create_test_user.id}",
        json={
            "name": "Updated Name",
            "address": "New Address",
            "phone_country_code": "+94",
            "phone_number": "771234567",
            "birthday": "1995-06-08",
            "gender": "prefer_not_to_say",
        },
        cookies=admin_cookie,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

def test_update_password_success(client, create_test_user, admin_cookie):
    response = client.put(
        f"/users/{create_test_user.id}/password",
        json={"current_password": "admin123", "new_password": "newpass456"},
        cookies=admin_cookie,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

def test_update_password_failure(client, create_test_user, admin_cookie):
    response = client.put(
        f"/users/{create_test_user.id}/password",
        json={"current_password": "wrongpass", "new_password": "newpass456"},
        cookies=admin_cookie,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect current password"


def test_profile_and_address_book(client, db_session):
    email = f"profile_{uuid.uuid4().hex[:6]}@gmail.com"
    user = User(
        name="Profile User",
        email=email,
        password=hash_password("profile123"),
        address="Old Address",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    login = client.post("/auth/login", json={"email": email, "password": "profile123"})
    cookie = {"jwt": login.cookies.get("jwt")}

    profile_response = client.put(
        "/users/me/profile",
        json={
            "name": "Profile Updated",
            "phone_country_code": "+1",
            "phone_number": "5551234567",
            "birthday": "1990-01-15",
            "gender": "other",
            "address": "Legacy summary",
        },
        cookies=cookie,
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["phone_country_code"] == "+1"

    create_address = client.post(
        "/users/me/addresses",
        json={
            "label": "Home",
            "recipient_name": "Profile Updated",
            "phone_country_code": "+1",
            "phone_number": "5551234567",
            "line1": "100 Main Street",
            "line2": "Apartment 4",
            "city": "Colombo",
            "state": "Western",
            "postal_code": "00100",
            "country": "Sri Lanka",
            "is_default": True,
        },
        cookies=cookie,
    )
    assert create_address.status_code == 200
    address_id = create_address.json()["id"]
    assert create_address.json()["is_default"] is True

    update_address_response = client.put(
        f"/users/me/addresses/{address_id}",
        json={"label": "Office", "city": "Kandy"},
        cookies=cookie,
    )
    assert update_address_response.status_code == 200
    assert update_address_response.json()["label"] == "Office"
    assert update_address_response.json()["city"] == "Kandy"

    list_response = client.get("/users/me/addresses", cookies=cookie)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/users/me/addresses/{address_id}", cookies=cookie)
    assert delete_response.status_code == 200
