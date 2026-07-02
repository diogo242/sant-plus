from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MedicalRecordBase(BaseModel):
    title: str
    record_type: str
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescription: Optional[str] = None
    medication: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    doctor_notes: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    appointment_id: Optional[str] = None


class MedicalRecordUpdate(MedicalRecordBase):
    doctor_id: Optional[str] = None
    hospital_id: Optional[str] = None
    is_encrypted: bool = True


class MedicalRecordOut(MedicalRecordBase):
    id: str
    patient_id: str
    doctor_id: Optional[str]
    hospital_id: Optional[str]
    is_encrypted: bool
    access_level: str
    hash_record: str
    is_anchored: bool
    bitcoin_tx_hash: Optional[str]
    anchored_at: Optional[datetime]
    version: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
