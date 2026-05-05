from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.finance import (
    InvoiceCreate, InvoiceResponse, InvoicePublic,
    PaymentCreate, PaymentResponse, PaymentWebhook,
)
from app.services.billing_service import (
    create_invoice, get_invoices, get_invoice_by_token,
    record_payment, process_webhook_payment,
)
from app.services.auth_service import get_current_active_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

admin_only = RoleChecker(["Admin"])
student_only = RoleChecker(["Student"])


# ----------------------------------------------------------------
#  Invoice Management
# ----------------------------------------------------------------

@router.post("/invoices", response_model=InvoiceResponse, dependencies=[Depends(admin_only)])
def generate_invoice(
    *,
    db: Session = Depends(get_db),
    invoice_in: InvoiceCreate,
) -> Any:
    """
    Generate a 1Bill-style invoice for a student.
    Creates a unique consumer number, bill reference, and payment link.
    """
    try:
        return create_invoice(db, invoice_data=invoice_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices", response_model=List[InvoiceResponse], dependencies=[Depends(admin_only)])
def list_invoices(
    db: Session = Depends(get_db),
    student_id: Optional[int] = Query(None),
    semester: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all invoices with optional filters (Admin only)."""
    return get_invoices(db, student_id=student_id, semester=semester, status=status, skip=skip, limit=limit)


@router.get("/invoices/me", response_model=List[InvoiceResponse], dependencies=[Depends(student_only)])
def my_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """View own invoices and payment status (Student only)."""
    return get_invoices(db, student_id=current_user.id)


@router.get("/invoices/pay/{token}", response_model=InvoicePublic)
def view_invoice_by_link(
    token: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    **Public endpoint** — no authentication required.
    View an invoice via its shareable payment link.
    Students receive this link to view and pay their fees.
    """
    invoice = get_invoice_by_token(db, token=token)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


# ----------------------------------------------------------------
#  Payment Recording
# ----------------------------------------------------------------

@router.post("/record", response_model=PaymentResponse, dependencies=[Depends(admin_only)])
def record_manual_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
) -> Any:
    """
    Manually record a payment (cash, bank transfer, etc.).
    Admin enters the details and the invoice is automatically updated.
    """
    payment, message = record_payment(db, payment_data=payment_in)
    if not payment:
        raise HTTPException(status_code=400, detail=message)
    return payment


# ----------------------------------------------------------------
#  1Bill Webhook Callback
# ----------------------------------------------------------------

@router.post("/webhook/1bill", response_model=PaymentResponse)
def onebill_webhook(
    *,
    db: Session = Depends(get_db),
    webhook_data: PaymentWebhook,
) -> Any:
    """
    **Public endpoint** — called by 1Bill when a student completes payment.

    Payload includes consumer_number, transaction_ref, and amount.
    The system finds the matching invoice and records the payment.
    """
    payment, message = process_webhook_payment(db, webhook_data=webhook_data)
    if not payment:
        raise HTTPException(status_code=400, detail=message)
    return payment
