from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Text,
    Boolean, Integer, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base
from backend.app.models.user import User, UserRole


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    npi = Column(String(100), unique=True, nullable=True, index=True)
    specialty = Column(String(100), nullable=False, index=True)
    sub_specialty = Column(String(100), nullable=True)
    license_number = Column(String(100), unique=True, nullable=True)
    years_experience = Column(Integer, default=0)
    consultation_price_xof = Column(Numeric(10, 2), nullable=True)
    consultation_price_sats = Column(Numeric(10, 2), nullable=True)
    bio = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="doctor")
    hospital = relationship("Hospital", back_populates="doctors")
    schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    invoices = relationship("Invoice", back_populates="doctor")


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday
    start_time = Column(String(5), nullable=False)  # "HH:MM"
    end_time = Column(String(5), nullable=False)
    is_available = Column(Boolean, default=True)
    max_patients = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("Doctor", back_populates="schedules")


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
