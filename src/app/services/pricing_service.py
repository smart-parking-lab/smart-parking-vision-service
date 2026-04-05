from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.pricing_rule import PricingRule
from app.models.vehicle import Vehicle
from app.models.vehicle_type import VehicleType
from app.utils.logger import get_logger

logger = get_logger("pricing_service")


def calculate_fee(db: Session, vehicle: Vehicle, duration_minutes: float) -> tuple[PricingRule | None, float]:
    """Tính phí đỗ xe."""
    if not vehicle or not vehicle.vehicle_type_id:
        return None, 5000.0 # Giá mặc định nếu không xác định được xe

    # Dùng timezone-aware now để lấy giờ hiện tại
    now = datetime.now(timezone.utc)
    current_time = now.strftime("%H:%M:%S")

    # Tìm Rule
    pricing_rule = db.query(PricingRule).filter(
        PricingRule.vehicle_type_id == vehicle.vehicle_type_id,
        PricingRule.is_active == True,
        current_time >= PricingRule.start_time,
        current_time <= PricingRule.end_time,
    ).order_by(PricingRule.priority.desc()).first()

    if not pricing_rule:
        return None, 5000.0

    if duration_minutes > 1440:
        amount = (duration_minutes / 1440) * pricing_rule.price_per_day
    else:
        amount = (duration_minutes / 60) * pricing_rule.price_per_hour

    return pricing_rule, round(float(amount), 0)
