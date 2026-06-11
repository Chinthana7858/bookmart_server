import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.utils import hash_password, require_admin
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.post("/", response_model=UserResponse)
def create_user_as_admin(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = (data.role or "user").strip().lower()
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        address=data.address,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/public-admin", response_model=UserResponse)
def create_admin_without_auth_for_dev(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    if os.getenv("ALLOW_PUBLIC_ADMIN_REGISTRATION", "false").lower() != "true":
        raise HTTPException(
            status_code=403,
            detail="Public admin registration is disabled",
        )

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        address=data.address,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
