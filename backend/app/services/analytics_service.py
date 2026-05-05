"""
Analytics Service — Reporting and dashboard data aggregation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.finance import Invoice, Payment, Payroll
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.course import Course, Enrollment
from app.schemas.finance import (
    RevenueSummary, AttendanceAnalytics, EnrollmentStats, PayrollSummary
)


def get_revenue_summary(db: Session):
    """Total collected vs outstanding fees, grouped by semester."""
    invoices = db.query(Invoice).all()

    # Group by semester
    semester_data = {}
    for inv in invoices:
        key = inv.semester
        if key not in semester_data:
            semester_data[key] = {
                "semester": key,
                "total_invoiced": 0.0,
                "total_collected": 0.0,
                "total_outstanding": 0.0,
                "invoice_count": 0,
                "paid_count": 0,
            }
        s = semester_data[key]
        s["total_invoiced"] += inv.total_amount
        s["total_collected"] += inv.amount_paid
        s["total_outstanding"] += max(0, inv.total_amount - inv.amount_paid)
        s["invoice_count"] += 1
        if inv.status == "Paid":
            s["paid_count"] += 1

    return [RevenueSummary(**v) for v in semester_data.values()]


def get_attendance_analytics(db: Session):
    """Per-course attendance rates and verification metrics."""
    courses = db.query(Course).all()
    results = []

    for course in courses:
        sessions = db.query(AttendanceSession).filter(
            AttendanceSession.course_id == course.id
        ).all()

        session_ids = [s.id for s in sessions]
        if not session_ids:
            results.append(AttendanceAnalytics(
                course_id=course.id,
                course_name=course.name,
                total_sessions=0,
                total_records=0,
                verified_count=0,
                remote_count=0,
                absent_count=0,
                verification_rate=0.0,
            ))
            continue

        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids)
        ).all()

        total = len(records)
        verified = sum(1 for r in records if r.is_verified)
        remote = sum(1 for r in records if r.status == "Remote")
        absent = sum(1 for r in records if r.status == "Absent")

        results.append(AttendanceAnalytics(
            course_id=course.id,
            course_name=course.name,
            total_sessions=len(sessions),
            total_records=total,
            verified_count=verified,
            remote_count=remote,
            absent_count=absent,
            verification_rate=round((verified / total * 100) if total > 0 else 0.0, 2),
        ))

    return results


def get_enrollment_stats(db: Session):
    """Student counts per course."""
    courses = db.query(Course).all()
    results = []

    for course in courses:
        count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()

        results.append(EnrollmentStats(
            course_id=course.id,
            course_name=course.name,
            course_code=course.code,
            student_count=count,
        ))

    return results


def get_payroll_summary(db: Session):
    """Total payroll expenses grouped by month."""
    payrolls = db.query(Payroll).all()

    month_data = {}
    for p in payrolls:
        key = p.month
        if key not in month_data:
            month_data[key] = {
                "month": key,
                "total_base": 0.0,
                "total_allowances": 0.0,
                "total_deductions": 0.0,
                "total_net": 0.0,
                "staff_count": 0,
            }
        m = month_data[key]
        m["total_base"] += p.base_salary
        m["total_allowances"] += p.allowances
        m["total_deductions"] += p.deductions
        m["total_net"] += p.net_salary
        m["staff_count"] += 1

    return [PayrollSummary(**v) for v in month_data.values()]
