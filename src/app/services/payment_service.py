from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.models.parking_session import ParkingSession
from app.utils.logger import get_logger

logger = get_logger("payment_service")


def handle_payment_confirmation(db: Session, invoice_id: str, session_id: str, mqtt_client):
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            logger.error(f"❌ Không tìm thấy invoice {invoice_id}")
            return

        if invoice.status == "paid":
            logger.warning(f"⚠️ Invoice {invoice_id} đã thanh toán trước đó")
            mqtt_client.publish_gate_open("GATE_OUT")
            return

        invoice.status = "paid"
        invoice.paid_at = datetime.now(timezone.utc) # Dùng aware datetime
        invoice.payment_method = "cash"

        session = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
        if session:
            session.status = "completed"

        db.commit()
        logger.info(f"✅ Thanh toán thành công: invoice={invoice_id}")
        mqtt_client.publish_gate_open("GATE_OUT")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Lỗi xử lý thanh toán: {e}")
        mqtt_client.publish_gate_open("GATE_OUT")
