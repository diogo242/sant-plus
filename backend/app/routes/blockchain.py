from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.medical import MedicalHash
from backend.app.models.bitcoin_transaction import BitcoinTransaction
from backend.app.models.invoice import Invoice
from backend.app.services.blockchain import generate_record_hash, mock_anchor_hash_to_bitcoin, validate_bitcoin_tx_hash
from datetime import datetime

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])


@router.post("/anchor-hash")
async def anchor_hash(payload: dict, db: AsyncSession = Depends(get_db)):
    medical_record_id = payload.get("medical_record_id")
    content = payload.get("content", "")
    if not medical_record_id:
        raise HTTPException(status_code=400, detail="medical_record_id requis")
    content_hash = payload.get("content_hash") or generate_record_hash(content)
    anchoring = mock_anchor_hash_to_bitcoin(medical_record_id, content_hash)
    mh = MedicalHash(
        medical_record_id=UUID(medical_record_id),
        sha256_hash=content_hash,
        bitcoin_tx_hash=anchoring["tx_hash"],
        bitcoin_tx_id=anchoring["tx_id"],
        testnet=True,
        anchored_at=datetime.utcnow(),
    )
    db.add(mh)
    await db.commit()
    await db.refresh(mh)
    return {
        "success": True,
        "medical_record_id": medical_record_id,
        "sha256_hash": content_hash,
        "tx_hash": anchoring["tx_hash"],
        "tx_id": anchoring["tx_id"],
        "network": "testnet",
        "blockchain_url": f"https://mempool.space/testnet/tx/{anchoring['tx_hash']}",
    }


@router.get("/verify-hash")
async def verify_hash(sha256_hash: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicalHash).where(MedicalHash.sha256_hash == sha256_hash))
    mh = result.scalar_one_or_none()
    if not mh:
        return {"found": False, "message": "Hash non enregistré"}
    return {
        "found": True,
        "medical_record_id": str(mh.medical_record_id),
        "sha256_hash": mh.sha256_hash,
        "anchored": mh.anchored,
        "bitcoin_tx_hash": mh.bitcoin_tx_hash,
        "anchored_at": mh.anchored_at.isoformat() if mh.anchored_at else None,
        "blockchain_url": f"https://mempool.space/testnet/tx/{mh.bitcoin_tx_hash}" if mh.bitcoin_tx_hash else None,
    }


@router.post("/verify-authenticity")
async def verify_authenticity(payload: dict, db: AsyncSession = Depends(get_db)):
    content = payload.get("content", "")
    expected_hash = payload.get("expected_hash")
    computed_hash = generate_record_hash(content)
    if not expected_hash:
        return {"authentic": False, "message": "Hash attendu manquant"}
    authentic = computed_hash == expected_hash
    return {
        "authentic": authentic,
        "computed_hash": computed_hash,
        "expected_hash": expected_hash,
    }


@router.get("/bitcoin-verify/{tx_hash}")
async def verify_bitcoin_tx(tx_hash: str):
    if not validate_bitcoin_tx_hash(tx_hash):
        raise HTTPException(status_code=400, detail="Hash Bitcoin invalide")
    return {
        "tx_hash": tx_hash,
        "network": "testnet",
        "confirmations": 1,
        "is_valid": True,
        "blockchain_url": f"https://mempool.space/testnet/tx/{tx_hash}",
    }


@router.post("/payments/lightning")
async def create_lightning(payload: dict, db: AsyncSession = Depends(get_db)):
    invoice_id = payload.get("invoice_id")
    amount_sats = payload.get("amount_sats")
    if not invoice_id or not amount_sats:
        raise HTTPException(status_code=400, detail="invoice_id et amount_sats requis")
    result = await db.execute(select(Invoice).where(Invoice.id == UUID(invoice_id)))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    payment_hash = f"ln_{uuid.uuid4().hex[:32]}"
    payment_request = f"lnbc{int(amount_sats)}u1p0{payment_hash[:16]}"
    pay = Payment(
        invoice_id=inv.id,
        amount_xof=inv.total_xof,
        amount_sats=float(amount_sats),
        payment_method="Lightning",
        status=PaymentStatus.PAID,
        tx_hash=payment_hash,
        paid_at=datetime.utcnow(),
    )
    btc = BitcoinTransaction(
        invoice_id=inv.id,
        tx_hash=payment_hash,
        tx_id=payment_hash,
        amount_xof=inv.total_xof,
        amount_sats=float(amount_sats),
        network="testnet",
        confirmations=1,
        is_confirmed=True,
        is_testnet=True,
    )
    inv.payment_status = PaymentStatus.PAID
    inv.payment_method = "Lightning"
    inv.tx_hash = payment_hash
    inv.paid_at = datetime.utcnow()
    inv.qr_code_url = f"lightning:{payment_request}"
    db.add(pay)
    db.add(btc)
    await db.commit()
    return {
        "success": True,
        "invoice_id": str(inv.id),
        "payment_hash": payment_hash,
        "payment_request": payment_request,
        "amount_sats": int(amount_sats),
        "status": "paid",
        "tx_hash": payment_hash,
        "blockchain_url": f"https://mempool.space/testnet/tx/{payment_hash}",
    }
