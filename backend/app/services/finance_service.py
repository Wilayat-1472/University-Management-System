"""
Finance Service — Fee structure management and payroll processing.
"""
from typing import Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.finance import FeeStructure, Payroll
from app.schemas.finance import FeeStructureCreate, PayrollCreate, PayrollStatusUpdate


# ---------------------------------------------------------------------------
#  Fee Structure CRUD
# ---------------------------------------------------------------------------

def create_fee_structure(db: Session, fee_data: FeeStructureCreate) -> FeeStructure:
    """Admin creates a fee item for a course or university-wide."""
    fee = FeeStructure(**fee_data.model_dump())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


def get_fee_structures(
    db: Session,
    course_id: Optional[int] = None,
    semester: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List fee structures with optional filters."""
    query = db.query(FeeStructure)
    if course_id is not None:
        query = query.filter(FeeStructure.course_id == course_id)
    if semester:
        query = query.filter(FeeStructure.semester == semester)
    return query.offset(skip).limit(limit).all()


def get_fee_structure(db: Session, fee_id: int) -> Optional[FeeStructure]:
    return db.query(FeeStructure).filter(FeeStructure.id == fee_id).first()


# ---------------------------------------------------------------------------
#  Payroll CRUD
# ---------------------------------------------------------------------------

def create_payroll(db: Session, payroll_data: PayrollCreate) -> Payroll:
    """Admin creates a payroll entry for a staff member."""
    net_salary = (
        payroll_data.base_salary
        + payroll_data.allowances
        - payroll_data.deductions
    )
    payroll = Payroll(
        staff_id=payroll_data.staff_id,
        month=payroll_data.month,
        base_salary=payroll_data.base_salary,
        allowances=payroll_data.allowances,
        deductions=payroll_data.deductions,
        net_salary=net_salary,
        remarks=payroll_data.remarks,
        status="Pending",
    )
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


def get_payrolls(
    db: Session,
    staff_id: Optional[int] = None,
    month: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List payroll records with optional filters."""
    query = db.query(Payroll)
    if staff_id:
        query = query.filter(Payroll.staff_id == staff_id)
    if month:
        query = query.filter(Payroll.month == month)
    if status:
        query = query.filter(Payroll.status == status)
    return query.order_by(Payroll.created_at.desc()).offset(skip).limit(limit).all()


def update_payroll_status(
    db: Session, payroll_id: int, status_update: PayrollStatusUpdate
) -> Tuple[Optional[Payroll], str]:
    """Update payroll status: Pending → Processed → Paid."""
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        return None, "Payroll record not found"

    valid_transitions = {
        "Pending": ["Processed"],
        "Processed": ["Paid"],
        "Paid": [],
    }

    allowed = valid_transitions.get(payroll.status, [])
    if status_update.status not in allowed:
        return None, f"Cannot transition from '{payroll.status}' to '{status_update.status}'"

    payroll.status = status_update.status
    if status_update.status == "Processed":
        payroll.processed_at = func.now()

    db.commit()
    db.refresh(payroll)
    return payroll, f"Status updated to {status_update.status}"
