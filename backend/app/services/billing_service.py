"""
Billing Service — 1Bill-style invoice generation and payment processing.

This module is designed to be pluggable: swap the internal methods with
real 1Bill API calls when merchant credentials are available.
"""
import uuid
import string
import random
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.finance import Invoice, InvoiceItem, Payment, FeeStructure
from app.schemas.finance import InvoiceCreate, PaymentCreate, PaymentWebhook
from app.config import settings


# ---------------------------------------------------------------------------
#  Invoice identifier generators
# ---------------------------------------------------------------------------

def generate_consumer_number(db: Session, student_id: int) -> str:
    """Generate a unique consumer number like UMS-2026-00042."""
    year = datetime.utcnow().year
    # Count existing invoices to create a sequential number
    count = db.query(Invoice).count() + 1
    return f"UMS-{year}-{count:05d}"


def generate_bill_reference(length: int = 12) -> str:
    """Generate a random alphanumeric bill reference."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_payment_token() -> str:
    """Generate a secure UUID4 token for the payment link."""
    return uuid.uuid4().hex


def build_payment_link(token: str) -> str:
    """
    Build the shareable payment link URL.
    In production, this would point to your frontend payment page.
    """
    # For local dev, point to the API endpoint directly
    base_url = "http://localhost:8000"
    return f"{base_url}{settings.API_PREFIX}/payments/invoices/pay/{token}"


# ---------------------------------------------------------------------------
#  Invoice CRUD
# ---------------------------------------------------------------------------

def create_invoice(
    db: Session,
    invoice_data: InvoiceCreate,
) -> Invoice:
    """
    Generate a 1Bill-style invoice for a student.
    Pulls fee amounts from the specified FeeStructure IDs.
    """
    # Fetch fee structures and calculate total
    fee_structures = (
        db.query(FeeStructure)
        .filter(FeeStructure.id.in_(invoice_data.fee_structure_ids))
        .all()
    )

    if not fee_structures:
        raise ValueError("No valid fee structures found for the given IDs")

    total_amount = sum(fs.amount for fs in fee_structures)

    # Generate identifiers
    consumer_number = generate_consumer_number(db, invoice_data.student_id)
    bill_reference = generate_bill_reference()
    payment_token = generate_payment_token()
    payment_link = build_payment_link(payment_token)

    # Determine due date
    due_date = invoice_data.due_date
    if not due_date and fee_structures[0].due_date:
        due_date = fee_structures[0].due_date

    # Create the invoice
    invoice = Invoice(
        student_id=invoice_data.student_id,
        consumer_number=consumer_number,
        bill_reference=bill_reference,
        payment_token=payment_token,
        payment_link=payment_link,
        total_amount=total_amount,
        amount_paid=0.0,
        due_date=due_date,
        semester=invoice_data.semester,
        status="Unpaid",
    )
    db.add(invoice)
    db.flush()  # Get the invoice.id

    # Create line items
    for fs in fee_structures:
        item = InvoiceItem(
            invoice_id=invoice.id,
            fee_structure_id=fs.id,
            description=f"{fs.fee_type}: {fs.description or fs.fee_type}",
            amount=fs.amount,
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoices(
    db: Session,
    student_id: Optional[int] = None,
    semester: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List invoices with optional filters."""
    query = db.query(Invoice)
    if student_id:
        query = query.filter(Invoice.student_id == student_id)
    if semester:
        query = query.filter(Invoice.semester == semester)
    if status:
        query = query.filter(Invoice.status == status)
    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


def get_invoice_by_token(db: Session, token: str) -> Optional[Invoice]:
    """Fetch an invoice by its payment link token (public access)."""
    return db.query(Invoice).filter(Invoice.payment_token == token).first()


def get_invoice_by_id(db: Session, invoice_id: int) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def get_invoice_by_consumer_number(db: Session, consumer_number: str) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.consumer_number == consumer_number).first()


# ---------------------------------------------------------------------------
#  Payment processing
# ---------------------------------------------------------------------------

def _update_invoice_status(invoice: Invoice):
    """Recalculate invoice status based on amount_paid vs total_amount."""
    if invoice.amount_paid >= invoice.total_amount:
        invoice.status = "Paid"
    elif invoice.amount_paid > 0:
        invoice.status = "Partially Paid"
    else:
        invoice.status = "Unpaid"


def record_payment(
    db: Session,
    payment_data: PaymentCreate,
) -> Tuple[Optional[Payment], str]:
    """Record a manual payment (admin action for cash/bank transfers)."""
    invoice = get_invoice_by_id(db, payment_data.invoice_id)
    if not invoice:
        return None, "Invoice not found"

    if invoice.status == "Cancelled":
        return None, "Cannot pay a cancelled invoice"

    # Generate a transaction ref if none provided
    txn_ref = payment_data.transaction_ref or f"MANUAL-{uuid.uuid4().hex[:8].upper()}"

    payment = Payment(
        invoice_id=invoice.id,
        student_id=invoice.student_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_ref=txn_ref,
        status="Completed",
        remarks=payment_data.remarks,
    )
    db.add(payment)

    # Update invoice totals
    invoice.amount_paid += payment_data.amount
    _update_invoice_status(invoice)

    db.commit()
    db.refresh(payment)
    return payment, "Payment recorded successfully"


def process_webhook_payment(
    db: Session,
    webhook_data: PaymentWebhook,
) -> Tuple[Optional[Payment], str]:
    """
    Process a payment callback from 1Bill.
    This is the endpoint 1Bill calls after a student pays.
    """
    # Find the invoice by consumer number
    invoice = get_invoice_by_consumer_number(db, webhook_data.consumer_number)
    if not invoice:
        return None, "Invoice not found for consumer number"

    # Check for duplicate transaction
    existing = db.query(Payment).filter(
        Payment.transaction_ref == webhook_data.transaction_ref
    ).first()
    if existing:
        return existing, "Payment already processed"

    payment = Payment(
        invoice_id=invoice.id,
        student_id=invoice.student_id,
        amount=webhook_data.amount,
        payment_method=webhook_data.payment_method,
        transaction_ref=webhook_data.transaction_ref,
        status="Completed",
    )
    db.add(payment)

    # Update invoice totals
    invoice.amount_paid += webhook_data.amount
    _update_invoice_status(invoice)

    db.commit()
    db.refresh(payment)
    return payment, "Payment processed via 1Bill"
