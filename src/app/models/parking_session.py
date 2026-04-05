import uuid
from sqlalchemy import Column, UUID, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    # Sửa từ vehicle_id sang plate_number để khớp thực tế DB Supabase
    plate_number = Column(Text, nullable=False) 
    
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    entry_image_url = Column(String(255), nullable=True)
    exit_image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
