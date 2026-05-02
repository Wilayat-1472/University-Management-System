from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

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


class AttendanceRecordBase(BaseModel):
    session_id: int
    verification_code: str # Student provides this to mark attendance

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordInDBBase(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: str
    marked_at: datetime
    ip_address: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AttendanceRecord(AttendanceRecordInDBBase):
    pass
