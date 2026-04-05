import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.models.parking_session import ParkingSession
from app.models.invoice import Invoice
from app.services.lpr_client import recognize_plate # Quay lại dùng Client gọi API ngoài
from app.services.pricing_service import calculate_fee
from app.utils.logger import get_logger

logger = get_logger("gate_service")

async def handle_entry(db: Session, mqtt_client):
    # Gọi API LPR bên ngoài
    lpr_result = await recognize_plate("entry")
    
    plate = lpr_result.get("plate", "UNKNOWN") if lpr_result else "UNKNOWN"
    image_url = lpr_result.get("image_url") if lpr_result else None

    logger.info(f"🚗 [Remote API] XE VÀO: plate={plate}")

    try:
        session = ParkingSession(
            plate_number=plate,
            entry_time=datetime.now(timezone.utc),
            status="active",
            entry_image_url=image_url,
        )
        db.add(session)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Lỗi DB: {e}")

    mqtt_client.publish_gate_open("GATE_IN")

async def handle_exit(db: Session, mqtt_client):
    # Gọi API LPR bên ngoài
    lpr_result = await recognize_plate("exit")
    if not lpr_result: return

    plate = lpr_result.get("plate", "UNKNOWN")
    image_url = lpr_result.get("image_url")

    logger.info(f"🚗 [Remote API] XE RA: plate={plate}")

    try:
        session = db.query(ParkingSession).filter(
            ParkingSession.plate_number == plate,
            ParkingSession.status == "active",
        ).order_by(ParkingSession.entry_time.desc()).first()

        if not session:
            mqtt_client.publish_gate_open("GATE_OUT")
            return

        now = datetime.now(timezone.utc)
        duration_minutes = (now - session.entry_time.replace(tzinfo=timezone.utc)).total_seconds() / 60
        
        vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate).first()
        pricing_rule, amount = calculate_fee(db, vehicle, duration_minutes) if vehicle else (None, 5000.0)

        session.exit_time = now
        session.status = "pending_payment"
        session.exit_image_url = image_url
        db.commit()

        invoice = Invoice(
            session_id=session.id,
            pricing_rule_id=pricing_rule.id if pricing_rule else None,
            duration_minutes=round(duration_minutes),
            amount=amount,
            status="unpaid",
        )
        db.add(invoice)
        db.commit()
        
        mqtt_client.publish_payment_request(str(session.id), str(invoice.id), str(int(amount)))
    except Exception as e:
        db.rollback()
        mqtt_client.publish_gate_open("GATE_OUT")
