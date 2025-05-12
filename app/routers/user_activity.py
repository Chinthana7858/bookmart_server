from typing import Optional
from fastapi import APIRouter, Cookie, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.product import ProductOut
from app.schemas.user_activity import UserActivityCreate, UserActivityResponse
from app.services import user_activity_service

router = APIRouter(prefix="/activities", tags=["UserActivity"])

@router.post("/", response_model=UserActivityResponse)
def create_activity(
    data: UserActivityCreate,
    guest_session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    print("Received data:", data)
    print("Session ID from cookie:", guest_session_id)
    return user_activity_service.log_user_activity(db, data, guest_session_id)


@router.get("/top-viewed-details", response_model=list[ProductOut])
def get_top_viewed_book_details(db: Session = Depends(get_db)):
    return user_activity_service.get_top_viewed_product_details(db)


@router.get("/", response_model=list[UserActivityResponse])
def fetch_all_activities(db: Session = Depends(get_db)):
    return user_activity_service.get_all_activities(db)

@router.get("/user/{user_id}", response_model=list[UserActivityResponse])
def fetch_by_user(user_id: int, db: Session = Depends(get_db)):
    return user_activity_service.get_activities_by_user(user_id, db)

@router.get("/session/{session_id}", response_model=list[UserActivityResponse])
def fetch_by_session(session_id: str, db: Session = Depends(get_db)):
    return user_activity_service.get_activities_by_session(session_id, db)