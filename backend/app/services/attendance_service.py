import math
import string
import random
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.attendance import AttendanceSession, AttendanceRecord, AttendanceHeartbeat
from app.models.course import Course, Enrollment
from app.models.user import User
from app.schemas.attendance import AttendanceSessionCreate, AttendanceRecordCreate, AttendanceHeartbeatCreate


# ---------------------------------------------------------------------------
#  Geofencing utility
# ---------------------------------------------------------------------------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance (in meters) between two GPS points
    using the Haversine formula.
    """
    R = 6_371_000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
#  Session management
# ---------------------------------------------------------------------------

def generate_verification_code(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def start_session(db: Session, session_data: AttendanceSessionCreate, instructor_id: int):
    code = generate_verification_code()

    db_session = AttendanceSession(
        course_id=session_data.course_id,
        instructor_id=instructor_id,
        verification_code=code,
        is_active=True
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def end_session(db: Session, session_id: int, instructor_id: int):
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id,
        AttendanceSession.instructor_id == instructor_id
    ).first()
    if session:
        session.is_active = False
        session.end_time = func.now()
        db.commit()
        db.refresh(session)
    return session


def get_session_records(db: Session, session_id: int):
    return db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()


# ---------------------------------------------------------------------------
#  Attendance marking – with multi-layered verification
# ---------------------------------------------------------------------------

def _determine_status_and_verification(
    record_data: AttendanceRecordCreate,
    course: Course,
    user: User,
) -> dict:
    """
    Run all verification checks and return a dict with:
      status, is_verified, distance_from_class
    """
    result = {
        "status": "Present",
        "is_verified": True,
        "distance_from_class": None,
    }

    # --- Check 1: Mock location ---
    if record_data.is_mock_location:
        result["status"] = "Absent"
        result["is_verified"] = False
        return result  # Immediately reject

    # --- Check 2: Device verification ---
    if record_data.device_id and user.device_mac_address:
        if record_data.device_id != user.device_mac_address:
            result["is_verified"] = False  # Suspicious device, still mark but flag

    # --- Check 3: Geofencing ---
    if (
        course.latitude is not None
        and course.longitude is not None
        and record_data.latitude is not None
        and record_data.longitude is not None
    ):
        distance = haversine_distance(
            record_data.latitude, record_data.longitude,
            course.latitude, course.longitude
        )
        result["distance_from_class"] = round(distance, 2)
        allowed = course.allowed_radius or 200.0

        if distance > allowed:
            result["status"] = "Remote"
            result["is_verified"] = False

    return result


def mark_attendance(
    db: Session,
    record_data: AttendanceRecordCreate,
    student_id: int,
    ip_address: str = None,
):
    # 1. Validate session
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == record_data.session_id,
        AttendanceSession.is_active == True
    ).first()

    if not session:
        return None, "Session not found or inactive"

    if session.verification_code != record_data.verification_code:
        return None, "Invalid verification code"

    # 2. Check enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.student_id == student_id
    ).first()

    if not enrollment:
        return None, "Student not enrolled in this course"

    # 3. Prevent duplicate marking
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == student_id
    ).first()

    if existing_record:
        return existing_record, "Attendance already marked"

    # 4. Run verification pipeline
    course = db.query(Course).filter(Course.id == session.course_id).first()
    user = db.query(User).filter(User.id == student_id).first()
    checks = _determine_status_and_verification(record_data, course, user)

    # 5. Persist the record
    db_record = AttendanceRecord(
        session_id=session.id,
        student_id=student_id,
        status=checks["status"],
        ip_address=ip_address,
        latitude=record_data.latitude,
        longitude=record_data.longitude,
        is_mock_location=record_data.is_mock_location,
        is_verified=checks["is_verified"],
        device_id=record_data.device_id,
        distance_from_class=checks["distance_from_class"],
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record, "Success"


# ---------------------------------------------------------------------------
#  Heartbeat – periodic location pings during a live session
# ---------------------------------------------------------------------------

def log_heartbeat(db: Session, heartbeat_data: AttendanceHeartbeatCreate, student_id: int):
    """Validate and store a heartbeat ping sent by the student's device."""

    # Verify the record exists and belongs to this student
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.id == heartbeat_data.record_id,
        AttendanceRecord.student_id == student_id,
    ).first()

    if not record:
        return None, "Attendance record not found or does not belong to you"

    # Verify the session is still active
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == record.session_id,
        AttendanceSession.is_active == True,
    ).first()

    if not session:
        return None, "Session is no longer active"

    # Check distance
    course = db.query(Course).filter(Course.id == session.course_id).first()
    is_within = True
    if (
        course.latitude is not None
        and course.longitude is not None
    ):
        distance = haversine_distance(
            heartbeat_data.latitude, heartbeat_data.longitude,
            course.latitude, course.longitude,
        )
        allowed = course.allowed_radius or 200.0
        is_within = distance <= allowed

        # If student moved out of range mid-session, downgrade verification
        if not is_within:
            record.is_verified = False
            record.status = "Remote"

    heartbeat = AttendanceHeartbeat(
        record_id=heartbeat_data.record_id,
        latitude=heartbeat_data.latitude,
        longitude=heartbeat_data.longitude,
        is_within_radius=is_within,
    )
    db.add(heartbeat)
    db.commit()
    db.refresh(heartbeat)
    return heartbeat, "Heartbeat logged"
