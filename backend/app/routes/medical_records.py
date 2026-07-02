from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.medical import MedicalRecord, MedicalHash
from backend.app.models.patient import Patient
from backend.app.models.access import Permission, AccessRequest
from backend.app.core.security import get_current_user
from backend.app.services.blockchain import mock_anchor_hash_to_bitcoin, generate_record_hash
from backend.app.schemas.medical import MedicalRecordCreate, MedicalRecordOut

router = APIRouter(prefix="/api/medical_records", tags=["medical_records"])


@router.get("", response_model=List[MedicalRecordOut])
async def list_records(
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    record_type: Optional[str] = None,
    anchored: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = select(MedicalRecord).where(MedicalRecord.deleted_at.is_(None))
    if current.role.value == "patient":
        result = await db.execute(select(Patient.id).where(Patient.user_id == current.id))
        p = result.scalar_one_or_none()
        if p:
            query = query.where(MedicalRecord.patient_id == p)
    else:
        if patient_id:
            query = query.where(MedicalRecord.patient_id == UUID(patient_id))
    if doctor_id:
        query = query.where(MedicalRecord.doctor_id == UUID(doctor_id))
    if record_type:
        query = query.where(MedicalRecord.record_type == record_type)
    if anchored is not None:
        query = query.where(MedicalRecord.is_anchored == anchored)
    query = query.order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{record_id}", response_model=MedicalRecordOut)
async def get_record(record_id: str, db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == UUID(record_id), MedicalRecord.deleted_at.is_(None)))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Dossier médical non trouvé")
    return rec


@router.post("", response_model=MedicalRecordOut)
async def create_record(payload: MedicalRecordCreate, db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    if current.role.value not in ("doctor", "hospital_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    content = f"{payload.title}|{payload.diagnosis}|{payload.prescription}|{payload.medication}"
    content_hash = generate_record_hash(content)
    rec = MedicalRecord(
        patient_id=UUID(payload.patient_id) if payload.patient_id else None,
        doctor_id=UUID(payload.doctor_id) if payload.doctor_id else None,
        hospital_id=UUID(payload.hospital_id) if payload.hospital_id else None,
        appointment_id=UUID(payload.appointment_id) if payload.appointment_id else None,
        title=payload.title,
        record_type=payload.record_type,
        symptoms=payload.symptoms,
        diagnosis=payload.diagnosis,
        treatment_plan=payload.treatment_plan,
        prescription=payload.prescription,
        medication=payload.medication,
        dosage=payload.dosage,
        frequency=payload.frequency,
        duration=payload.duration,
        follow_up_date=payload.follow_up_date,
        doctor_notes=payload.doctor_notes,
        is_encrypted=True,
        is_anchored=False,
        hash_record=content_hash,
        content_hash=content_hash,
        version=1,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


@router.post("/{record_id}/anchor")
async def anchor_record(record_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == UUID(record_id), MedicalRecord.deleted_at.is_(None)))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    if rec.is_anchored:
        return {"status": "already_anchored", "bitcoin_tx_hash": rec.bitcoin_tx_hash}
    anchoring = mock_anchor_hash_to_bitcoin(str(rec.id), rec.hash_record)
    rec.is_anchored = True
    rec.bitcoin_tx_hash = anchoring["tx_hash"]
    rec.anchored_at = datetime.utcnow()
    mh = MedicalHash(
        medical_record_id=rec.id,
        sha256_hash=rec.hash_record,
        bitcoin_tx_hash=anchoring["tx_hash"],
        bitcoin_tx_id=anchoring["tx_id"],
        testnet=True,
        anchored_at=datetime.utcnow(),
    )
    db.add(mh)
    await db.commit()
    return anchoring
