from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FeeStructure(Base):
    """Defines fee items that students owe (per course or university-wide)."""
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # null = university-wide
    semester = Column(String(20), nullable=False, index=True)  # e.g. "Fall-2026"
    fee_type = Column(String(50), nullable=False)  # Tuition, Lab, Library, Exam, Other
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", lazy="joined")
    invoice_items = relationship("InvoiceItem", back_populates="fee_structure")


class Invoice(Base):
    """1Bill-style invoice generated per student per semester."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 1Bill identifiers
    consumer_number = Column(String(30), unique=True, nullable=False, index=True)  # UMS-2026-00001
    bill_reference = Column(String(20), unique=True, nullable=False, index=True)   # alphanumeric ref
    payment_token = Column(String(64), unique=True, nullable=False, index=True)    # secure UUID for link
    payment_link = Column(String(500), nullable=True)  # shareable URL

    total_amount = Column(Float, nullable=False, default=0.0)
    amount_paid = Column(Float, nullable=False, default=0.0)
    due_date = Column(DateTime(timezone=True), nullable=True)
    semester = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="Unpaid")  # Unpaid, Partially Paid, Paid, Overdue, Cancelled

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("User", lazy="joined")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    """Line items on an invoice — each maps to a FeeStructure."""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id"), nullable=True)
    description = Column(String(300), nullable=False)
    amount = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    fee_structure = relationship("FeeStructure", back_populates="invoice_items")


class Payment(Base):
    """Records individual payments against an invoice."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Float, nullable=False)
    payment_method = Column(String(30), nullable=False, default="Cash")  # 1Bill, BankTransfer, Cash, JazzCash, EasyPaisa, Card
    transaction_ref = Column(String(100), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="Pending")  # Pending, Completed, Failed, Refunded
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    remarks = Column(String(500), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
    student = relationship("User")


class Payroll(Base):
    """Monthly salary records for staff (Faculty + Admin)."""
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String(10), nullable=False)  # e.g. "2026-05"
    base_salary = Column(Float, nullable=False, default=0.0)
    allowances = Column(Float, nullable=False, default=0.0)
    deductions = Column(Float, nullable=False, default=0.0)
    net_salary = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="Pending")  # Pending, Processed, Paid
    processed_at = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff = relationship("User", lazy="joined")
