import hashlib
import secrets
from datetime import datetime
from typing import Optional
from backend.app.core.security import sha256_hash


def generate_record_hash(content: str) -> str:
    return sha256_hash(content)


def generate_op_return_metadata(medical_record_id: str, content_hash: str) -> str:
    prefix = "SantePlus:" if True else "SantePlusMainnet:"
    metadata = f"{prefix}{medical_record_id}:{content_hash}"
    return metadata


def verify_record_integrity(content: str, expected_hash: str) -> bool:
    actual_hash = generate_record_hash(content)
    return actual_hash == expected_hash


def validate_bitcoin_tx_hash(tx_hash: str) -> bool:
    if not tx_hash:
        return False
    return len(tx_hash) == 64 and all(c in "0123456789abcdef" for c in tx_hash.lower())


def mock_anchor_hash_to_bitcoin(medical_record_id: str, content_hash: str) -> dict:
    metadata = generate_op_return_metadata(medical_record_id, content_hash)
    mock_tx_hash = hashlib.sha256(
        f"{metadata}:{datetime.utcnow().isoformat()}:{secrets.token_hex(16)}".encode()
    ).hexdigest()

    return {
        "success": True,
        "medical_record_id": medical_record_id,
        "content_hash": content_hash,
        "metadata": metadata,
        "tx_hash": mock_tx_hash,
        "tx_id": mock_tx_hash,
        "network": "testnet",
        "confirmations": 1,
        "anchored_at": datetime.utcnow().isoformat(),
        "block_height": 999999,
        "fee_sats": 500,
    }
