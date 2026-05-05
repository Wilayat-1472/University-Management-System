from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verification_code = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)

    course = relationship("Course")
    instructor = relationship("User")
    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="Present")  # Present, Late, Remote, Absent
    marked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50), nullable=True)

    # --- Phase 3: Verification fields ---
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_mock_location = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    device_id = Column(String(100), nullable=True)  # Cross-checked against User.device_mac_address
    distance_from_class = Column(Float, nullable=True)  # Calculated distance in meters

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("User")
    heartbeats = relationship("AttendanceHeartbeat", back_populates="record", cascade="all, delete-orphan")


class AttendanceHeartbeat(Base):
    """Periodic location pings sent by the student's device during a live session."""
    __tablename__ = "attendance_heartbeats"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("attendance_records.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_within_radius = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("AttendanceRecord", back_populates="heartbeats")
