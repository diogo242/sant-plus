from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("")
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    hospital_id: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
):
    query = select(Appointment).where(Appointment.deleted_at.is_(None))
    if current.role.value in ("patient", "doctor", "hospital_admin"):
        if current.role.value == "patient":
            # Récupérer le patient_id du user
            from backend.app.models.patient import Patient
            result = await db.execute(select(Patient.id).where(Patient.user_id == current.id))
            p = result.scalar_one_or_none()
            if p:
                query = query.where(Appointment.patient_id == p)
        elif current.role.value == "doctor":
            from backend.app.models.doctor import Doctor
            result = await db.execute(select(Doctor.id).where(Doctor.user_id == current.id))
            d = result.scalar_one_or_none()
            if d:
                query = query.where(Appointment.doctor_id == d)
    if patient_id:
        query = query.where(Appointment.patient_id == UUID(patient_id))
    if doctor_id:
        query = query.where(Appointment.doctor_id == UUID(doctor_id))
    if hospital_id:
        query = query.where(Appointment.hospital_id == UUID(hospital_id))
    if status:
        query = query.where(Appointment.status == status)
    if from_date:
        query = query.where(Appointment.scheduled_date >= from_date)
    if to_date:
        query = query.where(Appointment.scheduled_date <= to_date)
    query = query.order_by(Appointment.scheduled_date.desc())
    result = await db.execute(query)
    appts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "patient_id": str(a.patient_id),
            "doctor_id": str(a.doctor_id) if a.doctor_id else None,
            "hospital_id": str(a.hospital_id),
            "specialty": a.specialty,
            "reason": a.reason,
            "symptoms": a.symptoms,
            "scheduled_date": a.scheduled_date.isoformat() if a.scheduled_date else None,
            "end_time": a.end_time.isoformat() if a.end_time else None,
            "status": a.status,
            "notes": a.notes,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in appts
    ]


@router.post("")
async def create_appointment(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
):
    patient_id = payload.get("patient_id")
    doctor_id = payload.get("doctor_id")
    hospital_id = payload.get("hospital_id")
    scheduled_date = payload.get("scheduled_date")
    if not all([patient_id, hospital_id, scheduled_date]):
        raise HTTPException(status_code=400, detail="patient_id, hospital_id et scheduled_date sont requis")
    appt = Appointment(
        patient_id=UUID(patient_id),
        doctor_id=UUID(doctor_id) if doctor_id else None,
        hospital_id=UUID(hospital_id),
        specialty=payload.get("specialty"),
        reason=payload.get("reason"),
        symptoms=payload.get("symptoms"),
        scheduled_date=datetime.fromisoformat(scheduled_date),
        status=AppointmentStatus.PENDING,
        notes=payload.get("notes"),
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return {"id": str(appt.id), "status": appt.status, "scheduled_date": appt.scheduled_date.isoformat()}


@router.patch("/{appt_id}/status")
async def update_appointment_status(appt_id: str, payload: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.id == UUID(appt_id)))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    new_status = payload.get("status")
    if new_status not in ("pending", "confirmed", "cancelled", "completed", "no_show"):
        raise HTTPException(status_code=400, detail="Statut invalide")
    appt.status = new_status
    await db.commit()
    return {"id": str(appt.id), "status": appt.status}
