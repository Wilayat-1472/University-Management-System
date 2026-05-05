from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.finance import (
    FeeStructure, FeeStructureCreate,
    PayrollCreate, PayrollResponse, PayrollStatusUpdate,
)
from app.services.finance_service import (
    create_fee_structure, get_fee_structures,
    create_payroll, get_payrolls, update_payroll_status,
)
from app.services.auth_service import get_current_active_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

admin_only = RoleChecker(["Admin"])
admin_or_faculty = RoleChecker(["Admin", "Faculty"])


# ----------------------------------------------------------------
#  Fee Structure Management
# ----------------------------------------------------------------

@router.post("/fees", response_model=FeeStructure, dependencies=[Depends(admin_only)])
def create_fee(
    *,
    db: Session = Depends(get_db),
    fee_in: FeeStructureCreate,
) -> Any:
    """Create a new fee structure (Admin only)."""
    return create_fee_structure(db, fee_data=fee_in)


@router.get("/fees", response_model=List[FeeStructure], dependencies=[Depends(admin_or_faculty)])
def list_fees(
    db: Session = Depends(get_db),
    course_id: Optional[int] = Query(None),
    semester: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List fee structures with optional filters."""
    return get_fee_structures(db, course_id=course_id, semester=semester, skip=skip, limit=limit)


# ----------------------------------------------------------------
#  Payroll Management
# ----------------------------------------------------------------

@router.post("/payroll", response_model=PayrollResponse, dependencies=[Depends(admin_only)])
def create_payroll_entry(
    *,
    db: Session = Depends(get_db),
    payroll_in: PayrollCreate,
) -> Any:
    """Create a payroll entry for a staff member (Admin only)."""
    return create_payroll(db, payroll_data=payroll_in)


@router.get("/payroll", response_model=List[PayrollResponse], dependencies=[Depends(admin_only)])
def list_payrolls(
    db: Session = Depends(get_db),
    staff_id: Optional[int] = Query(None),
    month: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List payroll records with optional filters (Admin only)."""
    return get_payrolls(db, staff_id=staff_id, month=month, status=status, skip=skip, limit=limit)


@router.put("/payroll/{payroll_id}/status", response_model=PayrollResponse, dependencies=[Depends(admin_only)])
def update_payroll(
    payroll_id: int,
    *,
    db: Session = Depends(get_db),
    status_in: PayrollStatusUpdate,
) -> Any:
    """
    Update payroll status.
    Valid transitions: Pending → Processed → Paid.
    """
    payroll, message = update_payroll_status(db, payroll_id=payroll_id, status_update=status_in)
    if not payroll:
        raise HTTPException(status_code=400, detail=message)
    return payroll
