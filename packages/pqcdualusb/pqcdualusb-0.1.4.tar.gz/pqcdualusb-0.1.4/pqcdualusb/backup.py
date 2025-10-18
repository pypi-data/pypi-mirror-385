"""
Backup Operations Module
========================

Dual USB backup operations with post-quantum cryptography.

Provides secure backup and restore functionality across two USB devices
with quantum-resistant encryption and integrity verification.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from .crypto import _encrypt_backup
from .device import _device_id_for_path, _is_removable_path
from .storage import _atomic_write
from .audit import _audit
from .utils import ProgressReporter

BACKUP_DIR = ".system_backup"
BACKUP_SUFFIX = ".enc.json"

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_backup(token: bytes, passphrase: str, backup_root: Path, rotation: int = 0, progress_callback: Optional[ProgressReporter] = None) -> Path:
    """Write encrypted backup with optional progress reporting."""
    dev = _device_id_for_path(backup_root)
    if not _is_removable_path(backup_root):
        raise RuntimeError("Backup path does not appear to be a removable device")
    
    if progress_callback is None:
        progress_callback = ProgressReporter(description="Writing backup")
    
    progress_callback.set_total(len(token) + 1024)  # Approximate total for encryption overhead
    
    meta = {"sha3": hashlib.sha3_512(token).hexdigest(), "created_at": _now_iso(), "rotation": rotation, "backup_device": dev}
    
    progress_callback.update(len(token) // 2)  # Report progress during encryption
    payload = _encrypt_backup(token, passphrase, meta)
    
    progress_callback.update(len(token) // 2)  # Report remaining progress
    dst = backup_root / BACKUP_DIR / f"token{BACKUP_SUFFIX}"
    _atomic_write(dst, payload)
    
    progress_callback.finish()
    _audit("backup_written", {"file": str(dst), "device": dev})
    return dst

def _read_backup_meta(backup_file: Path) -> dict:
    data = json.loads(backup_file.read_text("utf-8"))
    return data.get("meta", {})

def restore_from_backup(backup_file: Path, restore_primary: Path, passphrase: str) -> tuple[Path, Path]:
    from .storage import write_token_primary # Defer import to avoid cycle
    from .crypto import _derive_key
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    data = json.loads(backup_file.read_text("utf-8"))
    meta = data["meta"]
    aead = data["aead"]
    salt = bytes.fromhex(data["kdf"]["salt"])
    key, _ = _derive_key(passphrase, salt)
    pt = AESGCM(key).decrypt(bytes.fromhex(aead["nonce"]), bytes.fromhex(aead["ct"]), json.dumps(meta, separators=(",", ":")).encode())
    return write_token_primary(pt, restore_primary)