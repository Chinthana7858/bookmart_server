from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserUpdate, PasswordUpdate, UserResponse
from app.services.user_service import (
    get_all_users, get_user_by_id, update_user, update_password
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(user_id, db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return update_user(user_id, data, db)

@router.put("/{user_id}/password")
def update_password_info(user_id: int, data: PasswordUpdate, db: Session = Depends(get_db)):
    return update_password(user_id, data, db)
