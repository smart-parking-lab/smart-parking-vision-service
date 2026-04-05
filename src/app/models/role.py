import uuid
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey
from app.models.base import Base
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(20), unique=True, nullable=False)
