from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from backend.app.database import get_db
from backend.app.models.hospital import Hospital
from backend.app.services.hospital_recommender import recommend_hospitals

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/hospitals")
async def search_hospitals(
    lat: float = Query(..., description="Latitude du patient"),
    lng: float = Query(..., description="Longitude du patient"),
    disease: Optional[str] = None,
    specialty: Optional[str] = None,
    urgency: str = "normal",
    emergency_only: bool = False,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    query = select(Hospital).where(Hospital.deleted_at.is_(None), Hospital.is_verified == True)
    if emergency_only:
        query = query.where(Hospital.emergency_available == True)
    if specialty:
        query = query.where(func.lower(Hospital.specialty) == func.lower(specialty))
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
    ranked = recommend_hospitals(lat, lng, specialty, urgency, hospitals, max_results=limit)
    justifications = []
    for r in ranked:
        reasons = []
        if r["specialty_match"]:
            reasons.append("Correspondance de spécialité")
        if r["distance_km"] < 2:
            reasons.append("Très proche")
        if r["rating"] >= 4.2:
            reasons.append("Excellente note")
        if r["estimated_waiting_minutes"] < 45:
            reasons.append("Temps d'attente faible")
        justifications.append({"reasons": reasons})
    return {"query": {"lat": lat, "lng": lng, "disease": disease, "specialty": specialty, "urgency": urgency}, "results": ranked, "count": len(ranked)}
