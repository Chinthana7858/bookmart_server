from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.utils import require_admin
from app.db import get_db
from app.schemas.admin_dashboard import AdminDashboardSummary
from app.services.admin_dashboard_service import get_admin_dashboard_summary

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/summary", response_model=AdminDashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    return get_admin_dashboard_summary(db)
