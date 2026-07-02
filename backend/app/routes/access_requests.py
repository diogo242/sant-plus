from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.access import AccessRequest, Permission, AccessRequestStatus
from backend.app.schemas.access import AccessRequestCreate, RevokeAccess
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/api/access-requests", tags=["access_requests"])


@router.get("")
async def list_requests(db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    result = await db.execute(select(AccessRequest).order_by(AccessRequest.created_at.desc()))
    reqs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "patient_id": str(r.patient_id),
            "doctor_id": str(r.doctor_id),
            "hospital_id": str(r.hospital_id) if r.hospital_id else None,
            "status": r.status,
            "reason": r.reason,
            "processed_at": r.processed_at.isoformat() if r.processed_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reqs
    ]


@router.post("")
async def create_request(payload: AccessRequestCreate, db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    req = AccessRequest(
        patient_id=UUID(payload.patient_id),
        doctor_id=UUID(payload.doctor_id),
        hospital_id=UUID(payload.hospital_id) if payload.hospital_id else None,
        reason=payload.reason,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return {"id": str(req.id), "status": req.status, "created_at": req.created_at.isoformat() if req.created_at else None}


@router.patch("/{req_id}/status")
async def update_status(req_id: str, payload: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AccessRequest).where(AccessRequest.id == UUID(req_id)))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    status = payload.get("status")
    if status not in ("pending", "approved", "rejected", "revoked"):
        raise HTTPException(status_code=400, detail="Statut invalide")
    req.status = status
    req.processed_at = datetime.utcnow()
    await db.commit()
    return {"id": str(req.id), "status": req.status, "processed_at": req.processed_at.isoformat() if req.processed_at else None}
