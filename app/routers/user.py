from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth.utils import require_admin, require_user
from app.db import get_db
from app.schemas.user import (
    PaginatedUsers,
    PasswordUpdate,
    UserAddressCreate,
    UserAddressResponse,
    UserAddressUpdate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    add_address,
    delete_address,
    get_all_users,
    get_profile,
    get_user_by_id,
    get_users_paginated,
    list_addresses,
    update_address,
    update_password,
    update_profile,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return get_all_users(db)


@router.get("/paginated", response_model=PaginatedUsers)
def list_users_paginated(
    skip: int = Query(0, ge=0),
    limit: int = Query(15, gt=0),
    role: Literal["user", "admin"] | None = Query(None),
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    return get_users_paginated(db, skip=skip, limit=limit, role=role)


@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(db: Session = Depends(get_db), current_user=Depends(require_user)):
    return get_profile(current_user.id, db)


@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return update_profile(current_user.id, data, db)


@router.get("/me/addresses", response_model=list[UserAddressResponse])
def get_my_addresses(db: Session = Depends(get_db), current_user=Depends(require_user)):
    return list_addresses(current_user.id, db)


@router.post("/me/addresses", response_model=UserAddressResponse)
def create_my_address(
    data: UserAddressCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return add_address(current_user.id, data, db)


@router.put("/me/addresses/{address_id}", response_model=UserAddressResponse)
def update_my_address(
    address_id: int,
    data: UserAddressUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return update_address(current_user.id, address_id, data, db)


@router.delete("/me/addresses/{address_id}")
def delete_my_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    return delete_address(current_user.id, address_id, db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    return get_user_by_id(user_id, db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    return update_user(user_id, data, db)

@router.put("/{user_id}/password")
def update_password_info(
    user_id: int,
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user),
):
    if current_user.id != user_id and (current_user.role or "").strip().lower() != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not allowed to update this password")
    return update_password(user_id, data, db)
