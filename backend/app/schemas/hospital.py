from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HospitalBase(BaseModel):
    name: str
    type: str
    address: str
    city: Optional[str] = None
    region: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    emergency_available: bool = False


class HospitalCreate(HospitalBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HospitalOut(HospitalBase):
    id: str
    rating: float
    reviews_count: int
    is_verified: bool
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
