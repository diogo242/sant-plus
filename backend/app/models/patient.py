from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base
from backend.app.models.user import User, UserRole


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    npi = Column(String(100), unique=True, nullable=True, index=True)  # Numéro Personnel d'Identification
    wallet_address = Column(String(255), unique=True, nullable=True)
    wallet_balance_xof = Column(Numeric(12, 2), default=0)
    wallet_balance_sats = Column(Numeric(12, 2), default=0)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")
    access_logs = relationship("AccessLog", back_populates="patient")


class PatientAuthDetail(Base):
    __tablename__ = "patient_auth_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    pin_hash = Column(String(255), nullable=True)
    two_factor_secret = Column(String(255), nullable=True)
    two_factor_enabled = Column(String(10), default="false")
    recovery_codes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
