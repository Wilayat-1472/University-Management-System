from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --------------- Session Schemas ---------------

class AttendanceSessionBase(BaseModel):
    course_id: int

class AttendanceSessionCreate(AttendanceSessionBase):
    pass

class AttendanceSessionInDBBase(AttendanceSessionBase):
    id: int
    instructor_id: int
    verification_code: str
    is_active: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class AttendanceSession(AttendanceSessionInDBBase):
    pass


# --------------- Record Schemas ---------------

class AttendanceRecordBase(BaseModel):
    session_id: int
    verification_code: str  # Student provides this to mark attendance

class AttendanceRecordCreate(AttendanceRecordBase):
    """Payload sent by the student's device when marking attendance."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_mock_location: bool = False  # Reported by the mobile app
    device_id: Optional[str] = None  # Device identifier for cross-checking

class AttendanceRecordInDBBase(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: str
    marked_at: datetime
    ip_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_mock_location: bool = False
    is_verified: bool = False
    device_id: Optional[str] = None
    distance_from_class: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class AttendanceRecord(AttendanceRecordInDBBase):
    pass


# --------------- Heartbeat Schemas ---------------

class AttendanceHeartbeatCreate(BaseModel):
    """Periodic ping sent by the student's device during a live session."""
    record_id: int
    latitude: float
    longitude: float

class AttendanceHeartbeatInDBBase(BaseModel):
    id: int
    record_id: int
    latitude: float
    longitude: float
    is_within_radius: bool
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class AttendanceHeartbeat(AttendanceHeartbeatInDBBase):
    pass
