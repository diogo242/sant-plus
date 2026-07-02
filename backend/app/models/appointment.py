from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Enum, Text,
    Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base


class AppointmentStatus(str):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    specialty = Column(String(100), nullable=True, index=True)
    reason = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default=AppointmentStatus.PENDING, index=True)
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")
    invoice = relationship("Invoice", back_populates="appointment", uselist=False)
