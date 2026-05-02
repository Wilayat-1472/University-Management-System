from sqlalchemy.orm import Session
from app.models.course import Course, Enrollment
from app.schemas.course import CourseCreate, CourseUpdate, EnrollmentCreate

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Course).offset(skip).limit(limit).all()

def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()

def create_course(db: Session, course: CourseCreate, instructor_id: int):
    db_course = Course(**course.model_dump(), instructor_id=instructor_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def enroll_student(db: Session, enrollment: EnrollmentCreate, student_id: int):
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.course_id == enrollment.course_id,
        Enrollment.student_id == student_id
    ).first()
    if existing:
        return existing
        
    db_enrollment = Enrollment(course_id=enrollment.course_id, student_id=student_id)
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def get_student_enrollments(db: Session, student_id: int):
    return db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
