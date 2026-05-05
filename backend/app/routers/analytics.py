from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.finance import (
    RevenueSummary, AttendanceAnalytics, EnrollmentStats, PayrollSummary,
)
from app.services.analytics_service import (
    get_revenue_summary, get_attendance_analytics,
    get_enrollment_stats, get_payroll_summary,
)
from app.middleware.rbac import RoleChecker

router = APIRouter()

admin_only = RoleChecker(["Admin"])
admin_or_faculty = RoleChecker(["Admin", "Faculty"])


@router.get("/revenue", response_model=List[RevenueSummary], dependencies=[Depends(admin_only)])
def revenue_summary(
    db: Session = Depends(get_db),
) -> Any:
    """Revenue summary: total invoiced vs collected vs outstanding, grouped by semester."""
    return get_revenue_summary(db)


@router.get("/attendance", response_model=List[AttendanceAnalytics], dependencies=[Depends(admin_or_faculty)])
def attendance_analytics(
    db: Session = Depends(get_db),
) -> Any:
    """Per-course attendance rates and verification metrics."""
    return get_attendance_analytics(db)


@router.get("/enrollments", response_model=List[EnrollmentStats], dependencies=[Depends(admin_or_faculty)])
def enrollment_stats(
    db: Session = Depends(get_db),
) -> Any:
    """Student enrollment counts per course."""
    return get_enrollment_stats(db)


@router.get("/payroll", response_model=List[PayrollSummary], dependencies=[Depends(admin_only)])
def payroll_summary(
    db: Session = Depends(get_db),
) -> Any:
    """Total payroll expenses grouped by month."""
    return get_payroll_summary(db)
