from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.parking_session import ParkingSession

router = APIRouter(prefix="/parking-sessions", tags=["Parking Sessions"])


@router.get("")
def get_all_sessions(db: Session = Depends(get_db)):
    """Lấy tất cả phiên đỗ xe (Dashboard gọi)."""
    sessions = db.query(ParkingSession).order_by(ParkingSession.created_at.desc()).all()
    return [_serialize_session(s) for s in sessions]


@router.get("/{session_id}")
def get_session_by_id(session_id: UUID, db: Session = Depends(get_db)):
    """Chi tiết phiên đỗ xe."""
    session = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
    if not session:
        return {"error": "Không tìm thấy phiên đỗ xe"}
    return _serialize_session(session)


@router.get("/active/list")
def get_active_sessions(db: Session = Depends(get_db)):
    """Lấy danh sách xe đang đỗ."""
    sessions = db.query(ParkingSession).filter(
        ParkingSession.status == "active"
    ).order_by(ParkingSession.entry_time.desc()).all()
    return [_serialize_session(s) for s in sessions]


def _serialize_session(session: ParkingSession) -> dict:
    return {
        "id": str(session.id),
        "vehicle_id": str(session.vehicle_id) if session.vehicle_id else None,
        "plate_number": session.plate_number,
        "entry_time": session.entry_time.isoformat() if session.entry_time else None,
        "exit_time": session.exit_time.isoformat() if session.exit_time else None,
        "status": session.status,
        "entry_image_url": session.entry_image_url,
        "exit_image_url": session.exit_image_url,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }
