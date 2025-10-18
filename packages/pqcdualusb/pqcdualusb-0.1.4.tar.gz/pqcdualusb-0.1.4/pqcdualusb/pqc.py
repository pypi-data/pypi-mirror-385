"""
pqc.py
==============================================
Post-Quantum Cryptography (PQC) utilities using python-oqs.
"""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict

try:
    import oqs  # type: ignore
    HAS_OQS = True
except ImportError:
    HAS_OQS = False

from .security import SecurityConfig, secure_zero_memory
from .utils import secure_temp_file

logger = logging.getLogger("dual_usb")

# ------------- PQC audit signing (Dilithium) -------------
_PQ_AUDIT_SK_PATH: Optional[Path] = None
_PQ_AUDIT_LEVEL: str = "Dilithium3"

def pq_available(level: str = "Dilithium3") -> bool:
    """Check if a specific PQC algorithm is available."""
    if not HAS_OQS:
        return False
    try:
        return oqs.Signature(level).is_enabled()
    except (AttributeError, Exception): # Use generic Exception for broader compatibility
        return False

def pq_generate_keypair(level: str = "Dilithium3") -> tuple[bytes, bytes]:
    """Generate a PQC keypair for the given algorithm level."""
    if not pq_available(level):
        raise RuntimeError(f"PQC algorithm {level} not available.")
    with oqs.Signature(level) as sig:
        pk = sig.generate_keypair()
        sk = sig.export_secret_key()
    return pk, sk

def pq_write_audit_keys(primary_root: Path, backup_root: Path, passphrase: str, level: str = "Dilithium3") -> dict:
    """Generate and write PQC audit keys to primary and (encrypted) backup."""
    from .crypto import _encrypt_backup  # Lazy import to avoid circular dependency
    
    pk, sk = pq_generate_keypair(level)
    
    # Write plaintext keys to primary
    sk_path = primary_root / f".{level.lower()}_audit.key"
    pk_path = primary_root / f".{level.lower()}_audit.pub"
    
    with secure_temp_file(prefix=f"{level}_") as tmp_sk:
        tmp_sk.write_bytes(sk)
        os.replace(tmp_sk, sk_path)
    sk_path.chmod(0o600)

    with secure_temp_file(prefix=f"{level}_pub_") as tmp_pk:
        tmp_pk.write_bytes(pk)
        os.replace(tmp_pk, pk_path)
    pk_path.chmod(0o600)

    # Write encrypted secret key to backup
    meta = {"description": f"PQC audit secret key ({level})", "created_at": _now_iso()}
    encrypted_sk = _encrypt_backup(sk, passphrase, meta)
    backup_path = backup_root / ".system_backup" / f"{level.lower()}_audit.key.enc.json"
    backup_path.parent.mkdir(exist_ok=True, parents=True)
    
    with secure_temp_file(prefix=f"{level}_backup_") as tmp_backup:
        tmp_backup.write_bytes(encrypted_sk)
        os.replace(tmp_backup, backup_path)
    
    secure_zero_memory(bytearray(sk))
    
    return {"sk": str(sk_path), "pk": str(pk_path), "backup": str(backup_path)}

def pq_enable_audit_signing(sk_path: Path, level: str = "Dilithium3") -> None:
    """Enable PQC audit signing by setting the global secret key path."""
    global _PQ_AUDIT_SK_PATH, _PQ_AUDIT_LEVEL
    if not sk_path.exists():
        raise FileNotFoundError(f"PQC secret key not found at {sk_path}")
    _PQ_AUDIT_SK_PATH = sk_path
    _PQ_AUDIT_LEVEL = level
    logger.info("PQC audit signing enabled (level: %s)", level)

def pq_sign(message: bytes, sk_path: Path, level: str = "Dilithium3") -> bytes:
    """Sign a message with the PQC secret key."""
    if not pq_available(level):
        raise RuntimeError(f"PQC algorithm {level} not available.")
    
    sk = sk_path.read_bytes()
    try:
        with oqs.Signature(level, sk) as sig:
            signature = sig.sign(message)
        return signature
    finally:
        secure_zero_memory(bytearray(sk))

def pq_verify(message: bytes, signature: bytes, pk: bytes, level: str = "Dilithium3") -> bool:
    """Verify a PQC signature."""
    if not pq_available(level):
        logger.error("PQC algorithm %s not available for verification.", level)
        return False
    try:
        with oqs.Signature(level) as sig:
            return sig.verify(message, signature, pk)
    except Exception as e:
        logger.error("PQC verification failed: %s", e)
        return False

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
