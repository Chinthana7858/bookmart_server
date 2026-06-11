import os

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.user import User, UserAddress
from app.auth.utils import hash_password, verify_password, create_access_token
from app.schemas.user import (
    PasswordUpdate,
    Token,
    UserAddressCreate,
    UserAddressUpdate,
    UserCreate,
    UserLogin,
    UserUpdate,
)


def _address_summary(address: UserAddressCreate | UserAddress | None):
    if not address:
        return None
    parts = [
        address.line1,
        address.line2,
        address.city,
        address.state,
        address.postal_code,
        address.country,
    ]
    return ", ".join(str(part) for part in parts if part)


def _clear_default_addresses(user_id: int, db: Session):
    db.query(UserAddress).filter(UserAddress.user_id == user_id).update(
        {UserAddress.is_default: False}
    )

def register_user(user: UserCreate, db: Session) -> Token:
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    requested_role = (user.role or "user").strip().lower()
    allow_public_admin = os.getenv("ALLOW_PUBLIC_ADMIN_REGISTRATION", "false").lower() == "true"
    role = requested_role if allow_public_admin and requested_role in {"user", "admin"} else "user"

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        address=user.address or _address_summary(user.primary_address),
        phone_country_code=user.phone_country_code,
        phone_number=user.phone_number,
        birthday=user.birthday,
        gender=user.gender,
        role=role
    )
    db.add(new_user)
    db.flush()
    if user.primary_address:
        address = UserAddress(
            user_id=new_user.id,
            **user.primary_address.model_dump(),
        )
        address.is_default = True
        db.add(address)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email, "role": new_user.role, "id": new_user.id})
    return {"access_token": token, "token_type": "bearer"}

def authenticate_user(user: UserLogin, db: Session) -> Token:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email, "role": (db_user.role or "").strip().lower(), "id": db_user.id,})
    return {"access_token": token, "token_type": "bearer"}

def get_all_users(db: Session):
    return db.query(User).all()

def get_users_paginated(db: Session, skip: int = 0, limit: int = 15, role: str | None = None):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.id.desc()).offset(skip).limit(limit).all()
    total = query.count()
    return {"users": users, "total": total}

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(user_id: int, data: UserUpdate, db: Session):
    user = get_user_by_id(user_id, db)
    user.name = data.name
    user.address = data.address
    user.phone_country_code = data.phone_country_code
    user.phone_number = data.phone_number
    user.birthday = data.birthday
    user.gender = data.gender
    db.commit()
    db.refresh(user)
    return user


def get_profile(user_id: int, db: Session):
    return get_user_by_id(user_id, db)


def update_profile(user_id: int, data: UserUpdate, db: Session):
    return update_user(user_id, data, db)


def list_addresses(user_id: int, db: Session):
    return (
        db.query(UserAddress)
        .filter(UserAddress.user_id == user_id)
        .order_by(UserAddress.is_default.desc(), UserAddress.id.asc())
        .all()
    )


def add_address(user_id: int, data: UserAddressCreate, db: Session):
    has_addresses = db.query(UserAddress).filter(UserAddress.user_id == user_id).first() is not None
    is_default = data.is_default or not has_addresses
    if is_default:
        _clear_default_addresses(user_id, db)

    payload = data.model_dump()
    payload["is_default"] = is_default
    address = UserAddress(user_id=user_id, **payload)
    db.add(address)
    db.flush()

    user = get_user_by_id(user_id, db)
    if address.is_default:
        user.address = _address_summary(address)
    db.commit()
    db.refresh(address)
    return address


def _get_owned_address(user_id: int, address_id: int, db: Session):
    address = (
        db.query(UserAddress)
        .filter(UserAddress.id == address_id, UserAddress.user_id == user_id)
        .first()
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


def update_address(user_id: int, address_id: int, data: UserAddressUpdate, db: Session):
    address = _get_owned_address(user_id, address_id, db)
    updates = data.model_dump(exclude_unset=True)
    if updates.get("is_default"):
        _clear_default_addresses(user_id, db)

    for field, value in updates.items():
        setattr(address, field, value)

    db.flush()
    user = get_user_by_id(user_id, db)
    if address.is_default:
        user.address = _address_summary(address)
    db.commit()
    db.refresh(address)
    return address


def delete_address(user_id: int, address_id: int, db: Session):
    address = _get_owned_address(user_id, address_id, db)
    was_default = address.is_default
    db.delete(address)
    db.flush()

    if was_default:
        next_address = (
            db.query(UserAddress)
            .filter(UserAddress.user_id == user_id)
            .order_by(UserAddress.id.asc())
            .first()
        )
        user = get_user_by_id(user_id, db)
        if next_address:
            next_address.is_default = True
            user.address = _address_summary(next_address)
        else:
            user.address = None

    db.commit()
    return {"message": "Address deleted successfully"}


def update_password(user_id: int, data: PasswordUpdate, db: Session):
    user = get_user_by_id(user_id, db)

    # Check if current password is correct
    if not verify_password(data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Update password
    user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

def get_orders_by_user(user_id: int, db: Session):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")
    return orders
