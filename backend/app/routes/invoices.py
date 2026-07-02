from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import uuid
from backend.app.database import get_db
from backend.app.models.invoice import Invoice, Payment, PaymentStatus, PaymentMethod
from backend.app.models.bitcoin_transaction import BitcoinTransaction
from backend.app.services.blockchain import generate_record_hash, mock_anchor_hash_to_bitcoin
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("")
async def create_invoice(payload: dict, db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    now = datetime.utcnow()
    inv = Invoice(
        invoice_number=f"INV-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
        patient_id=UUID(payload["patient_id"]),
        doctor_id=UUID(payload["doctor_id"]) if payload.get("doctor_id") else None,
        hospital_id=UUID(payload["hospital_id"]),
        appointment_id=UUID(payload["appointment_id"]) if payload.get("appointment_id") else None,
        patient_name=payload["patient_name"],
        patient_email=payload.get("patient_email"),
        doctor_name=payload.get("doctor_name"),
        hospital_name=payload["hospital_name"],
        hospital_address=payload.get("hospital_address"),
        services=str(payload.get("services", [])),
        subtotal_xof=float(payload.get("subtotal_xof", payload.get("total_xof", 0))),
        tax_xof=float(payload.get("tax_xof", 0)),
        total_xof=float(payload["total_xof"]),
        total_sats=float(payload.get("total_sats", 0)),
        payment_method=payload.get("payment_method", PaymentMethod.WALLET),
        payment_status=PaymentStatus.PENDING,
        due_date=now + timedelta(days=30),
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return {
        "id": str(inv.id),
        "invoice_number": inv.invoice_number,
        "patient_name": inv.patient_name,
        "hospital_name": inv.hospital_name,
        "total_xof": float(inv.total_xof),
        "total_sats": float(inv.total_sats) if inv.total_sats else None,
        "payment_status": inv.payment_status,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
    }


@router.get("")
async def list_invoices(db: AsyncSession = Depends(get_db), current=Depends(get_current_user), status: Optional[str] = None):
    query = select(Invoice)
    if status:
        query = query.where(Invoice.payment_status == status)
    query = query.order_by(Invoice.created_at.desc())
    result = await db.execute(query)
    invoices = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "invoice_number": i.invoice_number,
            "patient_id": str(i.patient_id),
            "patient_name": i.patient_name,
            "patient_email": i.patient_email,
            "doctor_id": str(i.doctor_id) if i.doctor_id else None,
            "doctor_name": i.doctor_name,
            "hospital_id": str(i.hospital_id),
            "hospital_name": i.hospital_name,
            "hospital_address": i.hospital_address,
            "services": i.services,
            "total_xof": float(i.total_xof),
            "total_sats": float(i.total_sats) if i.total_sats else None,
            "payment_method": i.payment_method,
            "payment_status": i.payment_status,
            "tx_hash": i.tx_hash,
            "qr_code_url": i.qr_code_url,
            "paid_at": i.paid_at.isoformat() if i.paid_at else None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "due_date": i.due_date.isoformat() if i.due_date else None,
        }
        for i in invoices
    ]


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == UUID(invoice_id)))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return {
        "id": str(inv.id),
        "invoice_number": inv.invoice_number,
        "patient_id": str(inv.patient_id),
        "patient_name": inv.patient_name,
        "patient_email": inv.patient_email,
        "doctor_id": str(inv.doctor_id) if inv.doctor_id else None,
        "doctor_name": inv.doctor_name,
        "hospital_id": str(inv.hospital_id),
        "hospital_name": inv.hospital_name,
        "hospital_address": inv.hospital_address,
        "services": inv.services,
        "total_xof": float(inv.total_xof),
        "total_sats": float(inv.total_sats) if inv.total_sats else None,
        "payment_method": inv.payment_method,
        "payment_status": inv.payment_status,
        "tx_hash": inv.tx_hash,
        "qr_code_url": inv.qr_code_url,
        "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
    }
