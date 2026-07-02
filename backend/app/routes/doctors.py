from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.doctor import Doctor
from backend.app.models.user import User

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.get("")
async def list_doctors(
    db: AsyncSession = Depends(get_db),
    hospital_id: Optional[str] = None,
    specialty: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Doctor).where(Doctor.deleted_at.is_(None), Doctor.is_available == True)
    if hospital_id:
        query = query.where(Doctor.hospital_id == hospital_id)
    if specialty:
        query = query.where(func.lower(Doctor.specialty) == func.lower(specialty))
    query = query.order_by(Doctor.years_experience.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    doctors = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "full_name": d.user.full_name if d.user else None,
            "email": d.user.email if d.user else None,
            "specialty": d.specialty,
            "sub_specialty": d.sub_specialty,
            "years_experience": d.years_experience,
            "consultation_price_xof": float(d.consultation_price_xof) if d.consultation_price_xof else None,
            "consultation_price_sats": float(d.consultation_price_sats) if d.consultation_price_sats else None,
            "is_available": d.is_available,
            "is_verified": d.is_verified,
            "bio": d.bio,
            "photo_url": d.photo_url,
            "hospital_id": str(d.hospital_id) if d.hospital_id else None,
            "npi": d.npi,
        }
        for d in doctors
    ]


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id, Doctor.deleted_at.is_(None)))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Médecin non trouvé")
    return {
        "id": str(d.id),
        "npi": d.npi,
        "specialty": d.specialty,
        "sub_specialty": d.sub_specialty,
        "years_experience": d.years_experience,
        "consultation_price_xof": float(d.consultation_price_xof) if d.consultation_price_xof else None,
        "consultation_price_sats": float(d.consultation_price_sats) if d.consultation_price_sats else None,
        "bio": d.bio,
        "photo_url": d.photo_url,
        "is_available": d.is_available,
        "is_verified": d.is_verified,
        "hospital_id": str(d.hospital_id) if d.hospital_id else None,
        "user": {
            "full_name": d.user.full_name if d.user else None,
            "email": d.user.email if d.user else None,
            "phone": d.user.phone if d.user else None,
        },
    }
