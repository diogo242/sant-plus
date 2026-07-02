from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Text,
    Boolean, Integer, Enum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base
from backend.app.models.user import User, UserRole


class HospitalType(str):
    PUBLIC = "public"
    PRIVATE = "private"
    CLINIC = "clinic"
    UNIVERSITY = "university"


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    country = Column(String(100), server_default="Bénin")
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_verified = Column(Boolean, default=False, index=True)
    rating = Column(Numeric(3, 2), default=0)
    reviews_count = Column(Integer, default=0)
    emergency_available = Column(Boolean, default=False)
    has_lab = Column(Boolean, default=False)
    has_radiology = Column(Boolean, default=False)
    has_pharmacy = Column(Boolean, default=False)
    has_ambulance = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    admin = relationship("User", back_populates="hospital_admin")
    doctors = relationship("Doctor", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")


class HospitalAdmin(Base):
    __tablename__ = "hospital_admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    position = Column(String(100), nullable=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "hospital_id", name="uq_hospital_admin"),)

    user = relationship("User", back_populates="hospital_admin")
    hospital = relationship("Hospital", back_populates="admins")

# Fix relation
Hospital.admins = relationship("HospitalAdmin", back_populates="hospital")


class HospitalService(Base):
    __tablename__ = "hospital_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_xof = Column(Numeric(10, 2), nullable=True)
    price_sats = Column(Numeric(10, 2), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HospitalReview(Base):
    __tablename__ = "hospital_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
