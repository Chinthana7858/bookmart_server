from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.auth.utils import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=Token)
def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    token_data = register_user(user, db)
    # response.set_cookie(
    #     key="jwt",
    #     value=token_data["access_token"],
    #     httponly=True,
    #     secure=True,  # Only over HTTPS in production
    #     samesite="None",
    #     max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # )
    return token_data

@router.post("/login", response_model=Token)
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    token_data = authenticate_user(user, db)
    response.set_cookie(
        key="jwt",
        value=token_data["access_token"],
        httponly=True,
        secure=True,
        samesite="None",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return token_data

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="jwt",
        path="/",
        httponly=True,
        secure=True,
        samesite="None"
    )
    response.delete_cookie(
        key="guest_session_id",
        path="/",
        httponly=True,
        secure=True,
        samesite="None"
    )
    return {"message": "Logged out"}

@router.get("/authenticate")
def get_logged_in_user(current_user = Depends(get_current_user)):
    return {
        "id":current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "name": current_user.name
    }
