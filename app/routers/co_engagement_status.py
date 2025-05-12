from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.CoEngagementStats import CoEngagementStatsOut
from app.services.co_engagement_update_service import get_all_co_engagement_stats


router = APIRouter()

@router.get("/co_engagement", response_model=list[CoEngagementStatsOut])
def read_co_engagement_stats(db: Session = Depends(get_db)):
    return get_all_co_engagement_stats(db)
