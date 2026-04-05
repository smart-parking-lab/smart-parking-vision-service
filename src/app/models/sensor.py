import uuid
from datetime import datetime
from sqlalchemy import Column, UUID, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    sensor_code = Column(String, unique=True, index=True)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("parking_slots.id"), index=True)
    status = Column(String, default="offline")
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    slot = relationship("ParkingSlot")
