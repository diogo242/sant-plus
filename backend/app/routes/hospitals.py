from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.hospital import Hospital
from backend.app.models.doctor import Doctor
from backend.app.models.hospital import HospitalService
from backend.app.models.user import User
from backend.app.services.hospital_recommender import recommend_hospitals
from backend.app.schemas.hospital import HospitalCreate, HospitalOut
from backend.app.core.security import get_current_user, require_user
from uuid import UUID

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("", response_model=List[HospitalOut])
async def list_hospitals(
    db: AsyncSession = Depends(get_db),
    city: Optional[str] = None,
    type: Optional[str] = None,
    emergency_only: bool = False,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Hospital).where(Hospital.deleted_at.is_(None))
    if city:
        query = query.where(func.lower(Hospital.city) == func.lower(city))
    if type:
        query = query.where(Hospital.type == type)
    if emergency_only:
        query = query.where(Hospital.emergency_available == True)
    query = query.order_by(Hospital.rating.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{hospital_id}", response_model=HospitalOut)
async def get_hospital(hospital_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hospital).where(Hospital.id == UUID(hospital_id), Hospital.deleted_at.is_(None)))
    h = result.scalar_one_or_none()
    if not h:
        raise HTTPException(status_code=404, detail="Hôpital non trouvé")
    return h


@router.post("", response_model=HospitalOut)
async def create_hospital(payload: HospitalCreate, current=Depends(require_user), db: AsyncSession = Depends(get_db)):
    if current.role.value not in ("hospital_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    h = Hospital(
        name=payload.name,
        type=payload.type,
        address=payload.address,
        city=payload.city,
        region=payload.region,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        description=payload.description,
        emergency_available=payload.emergency_available,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return h


@router.post("/recommend")
async def recommend_endpoint(
    lat: float = Query(..., description="Latitude du patient"),
    lng: float = Query(..., description="Longitude du patient"),
    specialty: Optional[str] = None,
    urgency: str = "normal",
    emergency_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    query = select(Hospital).where(Hospital.deleted_at.is_(None), Hospital.is_verified == True)
    if emergency_only:
        query = query.where(Hospital.emergency_available == True)
    result = await db.execute(query)
    hospitals = [{
        "id": str(h.id),
        "name": h.name,
        "lat": float(h.latitude) if h.latitude else None,
        "lng": float(h.longitude) if h.longitude else None,
        "rating": float(h.rating) if h.rating else 3.0,
        "services": [],
        "average_waiting_time": 60,
        "type": h.type,
        "address": h.address,
        "phone": h.phone,
        "is_verified": h.is_verified,
        "emergency_available": h.emergency_available,
    } for h in result.scalars().all()]
    ranked = recommend_hospitals(lat, lng, specialty, urgency, hospitals)
    return {"results": ranked, "count": len(ranked)}
