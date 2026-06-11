
import pytest
import uuid
from app.models.user import User
from app.auth.utils import hash_password
from tests.conftest import db_session

@pytest.fixture
def test_create_user(db_session):
    db_session.query(User).filter(User.email == "test@example.com").delete()
    db_session.commit()
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        address="123 Test St",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

#Correctly create user
def test_signup_success(client, db_session):
    response = client.post("/auth/signup", json={
        "name": "New User",
        "email": "newuser@example.com",
        "password": "Password123",
        "phone_country_code": "+94",
        "phone_number": "771234567",
        "birthday": "1998-04-20",
        "gender": "female",
        "primary_address": {
            "label": "Home",
            "line1": "456 New Street",
            "city": "Colombo",
            "country": "Sri Lanka",
            "is_default": True
        },
        "role": "user"
    })

    assert response.status_code == 200 or response.status_code == 201
    assert response.cookies.get("jwt") is not None
    data = response.json()
    assert "id" in data or "access_token" in data or "message" in data
    created_user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert created_user.phone_country_code == "+94"
    assert created_user.address == "456 New Street, Colombo, Sri Lanka"
    assert len(created_user.addresses) == 1

    auth_response = client.get(
        "/auth/authenticate",
        cookies={"jwt": response.cookies.get("jwt")},
    )
    assert auth_response.status_code == 200
    assert auth_response.json()["email"] == "newuser@example.com"

def test_signup_can_create_admin(client, db_session):
    email = f"role_check_{uuid.uuid4().hex}@example.com"
    response = client.post("/auth/signup", json={
        "name": "Role Check",
        "email": email,
        "password": "Password123",
        "address": "456 New Street",
        "role": "admin"
    })

    assert response.status_code == 200 or response.status_code == 201
    created_user = db_session.query(User).filter(User.email == email).first()
    assert created_user is not None
    assert created_user.role == "admin"

#Signup fail due to same email
def test_signup_fail(client,test_create_user, db_session):
    response = client.post("/auth/signup", json={
        "name": "New User",
        "email": "test@example.com",
        "password": "Password123",
        "address": "456 New Street",
        "role": "user"
    })

    assert response.status_code == 400 

#Correctly login
def test_login_success(client, test_create_user):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.cookies.get("jwt") is not None
    set_cookie = response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Secure" not in set_cookie

#Login fail due to incorrect credentials
def test_login_fail(client):
    response = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401 or response.status_code == 400

#Correctly logout
def test_logout(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

#Correctly authenticate
def test_authenticate_success(client, test_create_user, db_session):
    login_resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    cookies = login_resp.cookies

    response = client.get("/auth/authenticate", cookies={"jwt": cookies.get("jwt")})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()


#test without cookies
def test_authenticate_unauthorized(client):
    response = client.get("/auth/authenticate")
    assert response.status_code == 401 
