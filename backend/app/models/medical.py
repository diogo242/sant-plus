from sqlalchemy import (
    Column, String, Text, Numeric, DateTime, ForeignKey, Enum, Boolean, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=False)
    record_type = Column(String(50), nullable=False, index=True)  # consultation, prescription, lab, imaging, surgery
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)
    medication = Column(String(255), nullable=True)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    doctor_notes = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON array of URLs

    # Sécurité et intégrité
    is_encrypted = Column(Boolean, default=True)
    access_level = Column(String(50), default="private")
    hash_record = Column(String(64), unique=True, nullable=False, index=True)
    content_hash = Column(String(64), nullable=True)  # SHA-256 du contenu pour vérification

    # Blockchain
    is_anchored = Column(Boolean, default=False, index=True)
    bitcoin_tx_hash = Column(String(64), unique=True, nullable=True, index=True)
    anchored_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
    hashes = relationship("MedicalHash", back_populates="medical_record", cascade="all, delete-orphan")


class MedicalHash(Base):
    __tablename__ = "medical_hashes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False)
    sha256_hash = Column(String(64), unique=True, nullable=False, index=True)
    merkle_root = Column(String(64), nullable=True)
    anchored = Column(Boolean, default=False)
    bitcoin_tx_hash = Column(String(64), unique=True, nullable=True, index=True)
    bitcoin_tx_id = Column(String(64), nullable=True)
    testnet = Column(Boolean, default=True)
    anchored_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medical_record = relationship("MedicalRecord", back_populates="hashes")
