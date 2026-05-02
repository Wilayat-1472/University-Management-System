from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    AttendanceSession, AttendanceSessionCreate,
    AttendanceRecord, AttendanceRecordCreate
)
from app.services.attendance_service import start_session, mark_attendance
from app.services.auth_service import get_current_active_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

instructor_only = RoleChecker(["Instructor", "Admin"])
student_only = RoleChecker(["Student"])

@router.post("/sessions", response_model=AttendanceSession, dependencies=[Depends(instructor_only)])
def start_attendance_session(
    *,
    db: Session = Depends(get_db),
    session_in: AttendanceSessionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Start a new attendance session for a course. Generates verification code.
    """
    return start_session(db, session_data=session_in, instructor_id=current_user.id)

@router.post("/mark", response_model=AttendanceRecord, dependencies=[Depends(student_only)])
def mark_student_attendance(
    request: Request,
    *,
    db: Session = Depends(get_db),
    record_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Student marks their attendance using the verification code.
    """
    client_ip = request.client.host if request.client else None
    
    record, message = mark_attendance(
        db, 
        record_data=record_in, 
        student_id=current_user.id,
        ip_address=client_ip
    )
    
    if not record:
        raise HTTPException(status_code=400, detail=message)
        
    return record
