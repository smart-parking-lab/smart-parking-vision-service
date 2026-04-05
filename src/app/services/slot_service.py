from sqlalchemy.orm import Session
from app.models.parking_slot import ParkingSlot
from app.utils.logger import get_logger

logger = get_logger("slot_service")

def handle_slot_update(db: Session, sensor: str, status: str):
    """
    Cập nhật trạng thái slot khi nhận tín hiệu cảm biến (SYSTEM_DESIGN luồng slot).
    Nếu slot_code không tồn tại, tự động tạo mới (Auto-provisioning).
    """
    # Mapping mặc định: sensor 'SLOT_1' -> slot_code 'SLOT_1'
    # Bạn có thể thêm mapping chi tiết vào đây nếu tên sensor khác tên slot
    slot_code = sensor.strip()
    
    try:
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_code == slot_code).first()
        
        # Nếu chưa có slot này trong DB, tự động tạo mới
        if not slot:
            logger.info(f"🆕 Tự động tạo slot mới trong DB: {slot_code}")
            slot = ParkingSlot(
                slot_code=slot_code,
                status="available",
                position_x=0, 
                position_y=0
            )
            db.add(slot)
            db.flush() # Để có ID lấy ra nếu cần dùng

        new_status = "occupied" if status == "CO_XE" else "available"
        
        if slot.status != new_status:
            slot.status = new_status
            db.commit()
            logger.info(f"🅿️ Cập nhật Slot {slot_code}: {new_status}")
        else:
            # Không thay đổi trạng thái thì không ghi log/commit rác
            pass

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Lỗi cập nhật slot {slot_code}: {e}")
