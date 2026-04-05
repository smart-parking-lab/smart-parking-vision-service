from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.parking_slot import ParkingSlot

router = APIRouter(prefix="/parking-slots", tags=["Parking Slots"])


@router.get("")
def get_all_slots(db: Session = Depends(get_db)):
    """Lấy trạng thái tất cả slot (Dashboard gọi)."""
    slots = db.query(ParkingSlot).all()
    return [_serialize_slot(s) for s in slots]


def _serialize_slot(slot: ParkingSlot) -> dict:
    return {
        "id": str(slot.id),
        "slot_code": slot.slot_code,
        "status": slot.status,
        "position_x": slot.position_x,
        "position_y": slot.position_y,
        "created_at": slot.created_at.isoformat() if slot.created_at else None,
    }
