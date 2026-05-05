from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    credits: int = 3
    # Geofencing fields
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    allowed_radius: float = 200.0  # meters

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    allowed_radius: Optional[float] = None

class CourseInDBBase(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Course(CourseInDBBase):
    pass


class EnrollmentBase(BaseModel):
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentInDBBase(EnrollmentBase):
    id: int
    student_id: int
    enrolled_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Enrollment(EnrollmentInDBBase):
    pass
