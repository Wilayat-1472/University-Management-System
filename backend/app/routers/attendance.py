from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    AttendanceSession, AttendanceSessionCreate,
    AttendanceRecord, AttendanceRecordCreate,
    AttendanceHeartbeat, AttendanceHeartbeatCreate,
)
from app.services.attendance_service import (
    start_session, end_session, get_session_records,
    mark_attendance, log_heartbeat,
)
from app.services.auth_service import get_current_active_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

instructor_only = RoleChecker(["Faculty", "Admin"])
student_only = RoleChecker(["Student"])


# ----------------------------------------------------------------
#  Session management (Instructor / Admin)
# ----------------------------------------------------------------

@router.post("/sessions", response_model=AttendanceSession, dependencies=[Depends(instructor_only)])
def start_attendance_session(
    *,
    db: Session = Depends(get_db),
    session_in: AttendanceSessionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Start a new attendance session for a course.  Generates a random
    verification code that students must submit to mark attendance.
    """
    return start_session(db, session_data=session_in, instructor_id=current_user.id)


@router.put("/sessions/{session_id}/end", response_model=AttendanceSession, dependencies=[Depends(instructor_only)])
def end_attendance_session(
    session_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    End an active attendance session.  Only the instructor who started
    the session (or an admin) can end it.
    """
    session = end_session(db, session_id=session_id, instructor_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or you are not the instructor")
    return session


@router.get("/sessions/{session_id}/records", response_model=List[AttendanceRecord], dependencies=[Depends(instructor_only)])
def list_session_records(
    session_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Retrieve all attendance records for a given session, including
    verification status and distance data.
    """
    return get_session_records(db, session_id=session_id)


# ----------------------------------------------------------------
#  Student attendance marking (with verification)
# ----------------------------------------------------------------

@router.post("/mark", response_model=AttendanceRecord, dependencies=[Depends(student_only)])
def mark_student_attendance(
    request: Request,
    *,
    db: Session = Depends(get_db),
    record_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Student marks attendance.  The payload includes the verification code
    plus GPS coordinates and device info for multi-layered verification:

    1. **Mock Location Check** – if `is_mock_location` is `true`, the
       record is flagged as **Absent** and unverified.
    2. **Device Check** – `device_id` is compared against the user's
       registered `device_mac_address`.
    3. **Geofencing** – distance to the course location is calculated;
       if outside the allowed radius the record is marked **Remote**.
    """
    client_ip = request.client.host if request.client else None

    record, message = mark_attendance(
        db,
        record_data=record_in,
        student_id=current_user.id,
        ip_address=client_ip,
    )

    if not record:
        raise HTTPException(status_code=400, detail=message)

    return record


# ----------------------------------------------------------------
#  Heartbeat – periodic location pings during a live session
# ----------------------------------------------------------------

@router.post("/heartbeat", response_model=AttendanceHeartbeat, dependencies=[Depends(student_only)])
def send_heartbeat(
    *,
    db: Session = Depends(get_db),
    heartbeat_in: AttendanceHeartbeatCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Encrypted heartbeat endpoint.  The student's app should call this
    every 5-10 minutes during a live session with current GPS coordinates.

    If the student is detected outside the allowed radius, their
    attendance record is downgraded to **Remote / Unverified**.
    """
    heartbeat, message = log_heartbeat(
        db,
        heartbeat_data=heartbeat_in,
        student_id=current_user.id,
    )

    if not heartbeat:
        raise HTTPException(status_code=400, detail=message)

    return heartbeat
