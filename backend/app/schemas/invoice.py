from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InvoiceCreate(BaseModel):
    patient_id: str
    doctor_id: Optional[str] = None
    hospital_id: str
    appointment_id: Optional[str] = None
    services: List[dict]
    total_xof: float
    tax_xof: float = 0
    payment_method: Optional[str] = "Wallet"
    due_date: Optional[datetime] = None


class InvoiceUpdate(BaseModel):
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    tx_hash: Optional[str] = None


class InvoiceOut(BaseModel):
    id: str
    invoice_number: str
    patient_id: str
    patient_name: str
    patient_email: Optional[str]
    doctor_id: Optional[str]
    doctor_name: Optional[str]
    hospital_id: str
    hospital_name: str
    hospital_address: Optional[str]
    services: str
    subtotal_xof: Optional[float]
    tax_xof: Optional[float]
    total_xof: float
    total_sats: Optional[float]
    payment_method: Optional[str]
    payment_status: str
    tx_hash: Optional[str]
    qr_code_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: Optional[datetime]
    due_date: Optional[datetime]

    class Config:
        from_attributes = True
