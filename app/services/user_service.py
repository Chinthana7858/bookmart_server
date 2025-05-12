from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.user import User
from app.auth.utils import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserLogin, Token, UserUpdate, PasswordUpdate

def register_user(user: UserCreate, db: Session) -> Token:
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        address=user.address,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email, "role": new_user.role})
    return {"access_token": token, "token_type": "bearer"}

def authenticate_user(user: UserLogin, db: Session) -> Token:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email, "role": db_user.role, "id": db_user.id,})
    return {"access_token": token, "token_type": "bearer"}

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(user_id: int, data: UserUpdate, db: Session):
    user = get_user_by_id(user_id, db)
    user.name = data.name
    user.address = data.address
    db.commit()
    db.refresh(user)
    return user


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