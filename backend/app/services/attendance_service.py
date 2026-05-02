from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import string
import random
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.schemas.attendance import AttendanceSessionCreate, AttendanceRecordCreate
from app.models.course import Enrollment

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

def mark_attendance(db: Session, record_data: AttendanceRecordCreate, student_id: int, ip_address: str = None):
    # Check if session exists and is active
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == record_data.session_id,
        AttendanceSession.is_active == True
    ).first()
    
    if not session:
        return None, "Session not found or inactive"
        
    if session.verification_code != record_data.verification_code:
        return None, "Invalid verification code"
        
    # Check if student is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.student_id == student_id
    ).first()
    
    if not enrollment:
        return None, "Student not enrolled in this course"
        
    # Check if already marked
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == student_id
    ).first()
    
    if existing_record:
        return existing_record, "Attendance already marked"
        
    db_record = AttendanceRecord(
        session_id=session.id,
        student_id=student_id,
        status="Present",
        ip_address=ip_address
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record, "Success"

def get_session_records(db: Session, session_id: int):
    return db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()

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
