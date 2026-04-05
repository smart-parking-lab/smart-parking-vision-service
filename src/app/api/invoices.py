from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.invoice import Invoice

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("")
def get_all_invoices(db: Session = Depends(get_db)):
    """Lấy tất cả hoá đơn (Dashboard gọi)."""
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return [_serialize_invoice(inv) for inv in invoices]


@router.get("/{invoice_id}")
def get_invoice_by_id(invoice_id: UUID, db: Session = Depends(get_db)):
    """Chi tiết hoá đơn."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return {"error": "Không tìm thấy hoá đơn"}
    return _serialize_invoice(invoice)


def _serialize_invoice(invoice: Invoice) -> dict:
    return {
        "id": str(invoice.id),
        "session_id": str(invoice.session_id),
        "pricing_rule_id": str(invoice.pricing_rule_id) if invoice.pricing_rule_id else None,
        "duration_minutes": float(invoice.duration_minutes) if invoice.duration_minutes else None,
        "amount": float(invoice.amount) if invoice.amount else None,
        "status": invoice.status,
        "payment_method": invoice.payment_method,
        "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
    }
