import os

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.auth.utils import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


def _cookie_settings():
    explicit_secure = os.getenv("COOKIE_SECURE")
    secure = (
        explicit_secure.strip().lower() == "true"
        if explicit_secure is not None
        else os.getenv("FRONTEND_BASE_URL", "").strip().lower().startswith("https://")
    )
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "none" if secure else "lax",
        "path": "/",
    }


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="jwt",
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_cookie_settings(),
    )


def _delete_cookie(response: Response, key: str):
    response.delete_cookie(key=key, **_cookie_settings())


@router.post("/signup", response_model=Token)
def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    token_data = register_user(user, db)
    _set_auth_cookie(response, token_data["access_token"])
    return token_data

@router.post("/login", response_model=Token)
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    token_data = authenticate_user(user, db)
    _set_auth_cookie(response, token_data["access_token"])
    return token_data

@router.post("/logout")
def logout(response: Response):
    _delete_cookie(response, "jwt")
    _delete_cookie(response, "guest_session_id")
    return {"message": "Logged out"}

@router.get("/authenticate")
def get_logged_in_user(current_user = Depends(get_current_user)):
    return {
        "id":current_user.id,
        "email": current_user.email,
        "role": (current_user.role or "").strip().lower(),
        "name": current_user.name
    }
