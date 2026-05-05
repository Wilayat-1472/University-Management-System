from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course import Course, CourseCreate, Enrollment, EnrollmentCreate
from app.services.course_service import get_courses, create_course, enroll_student
from app.services.auth_service import get_current_active_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

instructor_or_admin = RoleChecker(["Faculty", "Admin"])
student_only = RoleChecker(["Student"])

@router.get("/", response_model=List[Course])
def read_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all courses.
    """
    return get_courses(db, skip=skip, limit=limit)

@router.post("/", response_model=Course, dependencies=[Depends(instructor_or_admin)])
def create_new_course(
    *,
    db: Session = Depends(get_db),
    course_in: CourseCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new course.
    """
    return create_course(db, course=course_in, instructor_id=current_user.id)

@router.post("/{course_id}/enroll", response_model=Enrollment, dependencies=[Depends(student_only)])
def enroll_in_course(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Enroll a student in a course.
    """
    enrollment_in = EnrollmentCreate(course_id=course_id)
    return enroll_student(db, enrollment=enrollment_in, student_id=current_user.id)
