import uuid
from sqlalchemy import Column, UUID, String, DateTime, ForeignKey, Float, Integer, Boolean, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class PricingRule(Base):
    __tablename__ = "pricing_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    vehicle_type_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_types.id"))
    price_per_hour = Column(Float, nullable=False)
    price_per_day = Column(Float, nullable=False)
    apply_after_minutes = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    days_of_week = Column(String(50), nullable=False)
    priority = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    vehicle_type = relationship("VehicleType")
