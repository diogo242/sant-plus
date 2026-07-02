from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AccessRequestCreate(BaseModel):
    patient_id: str
    doctor_id: str
    hospital_id: Optional[str] = None
    reason: Optional[str] = None


class AccessRequestOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    hospital_id: Optional[str]
    status: str
    reason: Optional[str]
    processed_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class PermissionGrant(BaseModel):
    patient_id: str
    doctor_id: str
    permission_type: str
    expires_at: Optional[datetime] = None


class RevokeAccess(BaseModel):
    permission_id: str
    reason: Optional[str] = None
