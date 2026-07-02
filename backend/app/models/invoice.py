from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.models.base import Base


class PaymentMethod(str):
    WALLET = "Wallet"
    LIGHTNING = "Lightning"
    BTC_ONCHAIN = "BTC_Onchain"
    CASH = "Cash"
    MOBILE_MONEY = "Mobile_Money"


class PaymentStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)

    patient_name = Column(String(255), nullable=False)
    patient_email = Column(String(255), nullable=True)
    doctor_name = Column(String(255), nullable=True)
    hospital_name = Column(String(255), nullable=False)
    hospital_address = Column(Text, nullable=True)

    services = Column(Text, nullable=False)  # JSON array of service names
    subtotal_xof = Column(Numeric(10, 2), nullable=True)
    tax_xof = Column(Numeric(10, 2), default=0)
    total_xof = Column(Numeric(10, 2), nullable=False, index=True)
    total_sats = Column(Numeric(12, 2), nullable=True)

    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(20), default=PaymentStatus.PENDING, index=True)
    tx_hash = Column(String(64), unique=True, nullable=True, index=True)
    lightning_invoice = Column(Text, nullable=True)
    qr_code_url = Column(String(500), nullable=True)

    paid_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient", back_populates="invoices")
    doctor = relationship("Doctor", back_populates="invoices")
    hospital = relationship("Hospital", backref="invoices")
    appointment = relationship("Appointment", back_populates="invoice")
    bitcoin_tx = relationship("BitcoinTransaction", back_populates="invoice", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_xof = Column(Numeric(10, 2), nullable=False)
    amount_sats = Column(Numeric(12, 2), nullable=True)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), default=PaymentStatus.PENDING)
    tx_hash = Column(String(64), unique=True, nullable=True, index=True)
    merchant_tx_id = Column(String(100), nullable=True)
    gateway = Column(String(50), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(String(255), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BitcoinTransaction(Base):
    __tablename__ = "bitcoin_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    tx_hash = Column(String(64), unique=True, nullable=False, index=True)
    tx_id = Column(String(64), unique=True, nullable=True, index=True)
    amount_xof = Column(Numeric(10, 2), nullable=True)
    amount_sats = Column(Numeric(12, 2), nullable=True)
    network = Column(String(20), default="testnet")
    confirmations = Column(Integer, default=0)
    is_confirmed = Column(Boolean, default=False)
    is_testnet = Column(Boolean, default=True)
    metadata_json = Column(Text, nullable=True)  # JSON string of on-chain metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    invoice = relationship("Invoice", back_populates="bitcoin_tx")
