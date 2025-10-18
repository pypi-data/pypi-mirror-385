"""
audit.py
==============================================
Tamper-evident audit logging.
"""
from __future__ import annotations

import os
import sys
import json
import time
import hmac
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Optional

from .security import SecurityConfig, secure_zero_memory
from .utils import AuditLogRotator
from .pqc import pq_sign, pq_verify, HAS_OQS

logger = logging.getLogger("dual_usb")

AUDIT_LOG_PATH = Path("pqcdualusb_audit.log")
AUDIT_KEY_PATH = Path(os.environ.get("PQC_DUALUSB_AUDIT_KEY", str(Path.home() / ".pqcdualusb_audit.key")))

if AUDIT_KEY_PATH.exists():
    AUDIT_KEY = AUDIT_KEY_PATH.read_bytes()
else:
    AUDIT_KEY = secrets.token_bytes(32)
    AUDIT_KEY_PATH.write_bytes(AUDIT_KEY)
    try:
        AUDIT_KEY_PATH.chmod(0o600)
    except Exception:
        pass

try:
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.touch(exist_ok=True)
    AUDIT_LOG_PATH.chmod(0o600)
except Exception:
    pass

_AUDIT_CHAIN: Optional[str] = None
_PQ_AUDIT_SK_PATH: Optional[Path] = None
_PQ_AUDIT_LEVEL: str = "Dilithium3"

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

_audit_rotator = AuditLogRotator(
    AUDIT_LOG_PATH,
    max_size=SecurityConfig.MAX_LOG_SIZE,
    max_files=SecurityConfig.MAX_LOG_FILES
)

def _audit(event: str, details: dict) -> None:
    """Append a tamper-evident line to the audit log."""
    global _AUDIT_CHAIN
    if _audit_rotator.should_rotate():
        _audit_rotator.rotate()

    safe = {k: ("<bytes>" if isinstance(v, (bytes, bytearray)) else v) for k, v in (details or {}).items()}
    base = f"{_now_iso()}|{event}|{json.dumps(safe, separators=(',',':'))}|prev={_AUDIT_CHAIN or ''}"

    mac = hmac.new(AUDIT_KEY, base.encode(), hashlib.sha256).hexdigest()
    chain_input = base + "|hmac=" + mac
    _AUDIT_CHAIN = hashlib.sha3_512(chain_input.encode()).hexdigest()

    pq_sig_hex = None
    pq_alg = None
    if HAS_OQS and _PQ_AUDIT_SK_PATH and _PQ_AUDIT_SK_PATH.exists():
        try:
            pq_sig_hex = pq_sign(chain_input.encode(), _PQ_AUDIT_SK_PATH, _PQ_AUDIT_LEVEL).hex()
            pq_alg = _PQ_AUDIT_LEVEL
        except Exception as e:
            logger.warning("PQ audit signing unavailable: %s", e)

    line = chain_input
    if pq_sig_hex:
        line += f"|pq_sig={pq_sig_hex}|pq_alg={pq_alg}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())
            break
        except OSError as e:
            if attempt == max_retries - 1:
                print(f"WARNING: Failed to write audit log after {max_retries} attempts: {e}", file=sys.stderr)
            else:
                time.sleep(0.1)

def verify_audit_log(pq_pk_path: Optional[Path] = None) -> bool:
    """Verify audit log integrity."""
    try:
        lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return False

    pk = None
    if pq_pk_path is not None:
        if not HAS_OQS:
            logger.error("PQ verify requested but python-oqs not available")
            return False
        try:
            pk = pq_pk_path.read_bytes()
        except Exception as e:
            logger.error("Failed to load PQ public key: %s", e)
            return False

    prev_chain = ""
    for raw in lines:
        parts = raw.split("|")
        try:
            prev_field = next((p for p in parts if p.startswith("prev=")), None)
            hmac_field = next((p for p in parts if p.startswith("hmac=") or p.startswith("sig=")), None)
            pq_sig_field = next((p for p in parts if p.startswith("pq_sig=")), None)
            if hmac_field is None or prev_field is None:
                logger.error("Audit line missing required fields: %s", raw)
                return False
            hmac_idx = parts.index(hmac_field)
            base = "|".join(parts[:hmac_idx]).rstrip("|")
            if prev_chain and ("prev=" + prev_chain) not in parts:
                logger.error("Audit chain mismatch")
                return False
            expect_mac = hmac.new(AUDIT_KEY, base.encode(), hashlib.sha256).hexdigest()
            got_mac = hmac_field.split("=", 1)[1]
            if got_mac != expect_mac:
                logger.error("Audit HMAC mismatch")
                return False
            chain_input = base + "|" + hmac_field
            prev_chain = hashlib.sha3_512(chain_input.encode()).hexdigest()
            if pk and pq_sig_field:
                sig_hex = pq_sig_field.split("=", 1)[1]
                if not pq_verify(chain_input.encode(), bytes.fromhex(sig_hex), pk, _PQ_AUDIT_LEVEL):
                    logger.error("Audit PQ signature verification failed")
                    return False
        except Exception:
            return False
    return True

import atexit
def _cleanup_sensitive_data():
    """Cleanup function called on program exit."""
    global AUDIT_KEY
    if AUDIT_KEY:
        secure_zero_memory(bytearray(AUDIT_KEY))

atexit.register(_cleanup_sensitive_data)
