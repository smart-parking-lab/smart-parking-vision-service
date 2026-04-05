import uuid
from sqlalchemy import Column, UUID, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.base import Base


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
