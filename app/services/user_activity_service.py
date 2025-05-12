
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate
from fastapi import HTTPException


def log_user_activity(db: Session, data: UserActivityCreate, session_id: str):
    activity = UserActivity(**data.dict(), session_id=session_id)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_top_viewed_product_details(db: Session, limit: int = 10):
    from app.models.product import Product

    subquery = (
        db.query(UserActivity.product_id, func.count(UserActivity.id).label("view_count"))
        .filter(UserActivity.action == "view")
        .group_by(UserActivity.product_id)
        .order_by(func.count(UserActivity.id).desc())
        .limit(limit)
        .subquery()
    )

    products = (
        db.query(Product)
        .join(subquery, Product.id == subquery.c.product_id)
        .order_by(subquery.c.view_count.desc())
        .all()
    )
    return products


def get_all_activities(db: Session):
    return db.query(UserActivity).all()

def get_activities_by_user(user_id: int, db: Session):
    return db.query(UserActivity).filter(UserActivity.user_id == user_id).all()

def get_activities_by_session(session_id: str, db: Session):
    return db.query(UserActivity).filter(UserActivity.session_id == session_id).all()