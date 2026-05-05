from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ======================== Fee Structure ========================

class FeeStructureBase(BaseModel):
    course_id: Optional[int] = None
    semester: str
    fee_type: str  # Tuition, Lab, Library, Exam, Other
    amount: float
    due_date: Optional[datetime] = None
    description: Optional[str] = None

class FeeStructureCreate(FeeStructureBase):
    pass

class FeeStructure(FeeStructureBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ======================== Invoice Items ========================

class InvoiceItemBase(BaseModel):
    fee_structure_id: Optional[int] = None
    description: str
    amount: float

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    model_config = ConfigDict(from_attributes=True)


# ======================== Invoice ========================

class InvoiceCreate(BaseModel):
    """Admin generates an invoice for a student."""
    student_id: int
    semester: str
    fee_structure_ids: List[int]  # Which fee items to include
    due_date: Optional[datetime] = None

class InvoiceResponse(BaseModel):
    id: int
    student_id: int
    consumer_number: str
    bill_reference: str
    payment_link: Optional[str] = None
    total_amount: float
    amount_paid: float
    due_date: Optional[datetime] = None
    semester: str
    status: str
    items: List[InvoiceItem] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InvoicePublic(BaseModel):
    """What the student sees via the payment link (no auth required)."""
    consumer_number: str
    bill_reference: str
    total_amount: float
    amount_paid: float
    due_date: Optional[datetime] = None
    semester: str
    status: str
    items: List[InvoiceItem] = []
    model_config = ConfigDict(from_attributes=True)


# ======================== Payment ========================

class PaymentCreate(BaseModel):
    """Admin manually records a payment (cash/bank)."""
    invoice_id: int
    amount: float
    payment_method: str = "Cash"  # Cash, BankTransfer, 1Bill, JazzCash, EasyPaisa, Card
    transaction_ref: Optional[str] = None
    remarks: Optional[str] = None

class PaymentWebhook(BaseModel):
    """Payload received from 1Bill callback."""
    consumer_number: str
    transaction_ref: str
    amount: float
    payment_method: str = "1Bill"

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    student_id: int
    amount: float
    payment_method: str
    transaction_ref: Optional[str] = None
    status: str
    paid_at: datetime
    remarks: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ======================== Payroll ========================

class PayrollBase(BaseModel):
    staff_id: int
    month: str  # e.g. "2026-05"
    base_salary: float
    allowances: float = 0.0
    deductions: float = 0.0
    remarks: Optional[str] = None

class PayrollCreate(PayrollBase):
    pass

class PayrollStatusUpdate(BaseModel):
    status: str  # Pending, Processed, Paid

class PayrollResponse(PayrollBase):
    id: int
    net_salary: float
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ======================== Analytics ========================

class RevenueSummary(BaseModel):
    semester: str
    total_invoiced: float
    total_collected: float
    total_outstanding: float
    invoice_count: int
    paid_count: int

class AttendanceAnalytics(BaseModel):
    course_id: int
    course_name: str
    total_sessions: int
    total_records: int
    verified_count: int
    remote_count: int
    absent_count: int
    verification_rate: float  # percentage

class EnrollmentStats(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    student_count: int

class PayrollSummary(BaseModel):
    month: str
    total_base: float
    total_allowances: float
    total_deductions: float
    total_net: float
    staff_count: int
