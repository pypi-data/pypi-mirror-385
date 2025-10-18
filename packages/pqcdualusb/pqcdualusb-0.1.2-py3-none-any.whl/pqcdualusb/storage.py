"""
storage.py
==============================================
File system and state management operations.
"""
from __future__ import annotations

import os
import json
import time
import tempfile
import hashlib
import hmac
from pathlib import Path
from typing import Dict

from .audit import _audit, AUDIT_KEY
from .device import _device_id_for_path

STATE_FILE = ".dual_usb_state.json"

def _fsync_dir(d: Path) -> None:
    try:
        fd = os.open(str(d), os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except Exception:
        pass

def _atomic_write(dst: Path, data: bytes) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=str(dst.parent), delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, dst)
    _fsync_dir(dst.parent)

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def _state_path(primary_root: Path) -> Path:
    return primary_root / STATE_FILE

def _state_mac(obj: dict) -> str:
    payload = {
        "rotation": int((obj or {}).get("rotation", 0)),
        "created_at": (obj or {}).get("created_at", ""),
        "device": (obj or {}).get("device", {}),
    }
    data = json.dumps(payload, separators=(",", ":")).encode()
    return hmac.new(AUDIT_KEY, data, hashlib.sha256).hexdigest()

def _state_load(primary_root: Path) -> dict:
    p = _state_path(primary_root)
    if not p.exists():
        obj = {"rotation": 0, "created_at": _now_iso(), "device": _device_id_for_path(primary_root)}
        obj["mac"] = _state_mac(obj)
        return obj
    try:
        obj = json.loads(p.read_text("utf-8"))
        if obj.get("mac") != _state_mac(obj):
            __import__("logging").getLogger("dual_usb").warning("primary state MAC mismatch; treating as rotation=0")
            obj = {"rotation": 0, "created_at": _now_iso(), "device": _device_id_for_path(primary_root)}
            obj["mac"] = _state_mac(obj)
        return obj
    except Exception:
        obj = {"rotation": 0, "created_at": _now_iso(), "device": _device_id_for_path(primary_root)}
        obj["mac"] = _state_mac(obj)
        return obj

def _state_save(primary_root: Path, rotation: int) -> None:
    payload = {"rotation": int(rotation), "created_at": _now_iso(), "device": _device_id_for_path(primary_root)}
    payload["mac"] = _state_mac(payload)
    _atomic_write(_state_path(primary_root), json.dumps(payload, separators=(",", ":")).encode())

def write_token_primary(token: bytes, primary_root: Path) -> tuple[Path, Path]:
    """Write plaintext token only to primary USB (USB-only) and record device identity."""
    fn = f"token_{int(time.time())}.bin"
    token_path = primary_root / fn
    dev = _device_id_for_path(primary_root)
    meta = {"created_at": _now_iso(), "sha3": hashlib.sha3_512(token).hexdigest(), "device": dev}
    _atomic_write(token_path, token)
    meta_path = primary_root / f"{fn}.meta.json"
    _atomic_write(meta_path, json.dumps(meta, separators=(",", ":")).encode())
    st = _state_load(primary_root)
    if st.get("rotation") is None:
        _state_save(primary_root, 0)
    _audit("primary_written", {"file": str(token_path), "device": dev})
    return token_path, meta_path

def verify_primary_binding(primary_token_path: Path, enforce: bool = True) -> bool:
    meta_path = primary_token_path.with_name(primary_token_path.name + ".meta.json")
    if not meta_path.exists():
        return not enforce
    try:
        meta = json.loads(meta_path.read_text("utf-8"))
        recorded = (meta.get("device") or {})
        current = _device_id_for_path(primary_token_path)
        rec_uuid = (recorded.get("uuid") or "").lower() or None
        cur_uuid = (current.get("uuid") or "").lower() or None
        if rec_uuid and cur_uuid:
            ok = rec_uuid == cur_uuid
        else:
            ok = True
            for key in ("label", "fs"):
                rv = recorded.get(key)
                cv = current.get(key)
                if rv and cv and rv != cv:
                    ok = False
                    break
        return ok or (not enforce)
    except Exception:
        return not enforce

def rotate_token(token: bytes, primary_mount: Path, backup_mount: Path, passphrase: str, prev_rotation: int) -> dict:
    from .backup import write_backup
    st = _state_load(primary_mount)
    current_rotation = st.get("rotation", 0)
    if current_rotation != prev_rotation:
        __import__("logging").getLogger("dual_usb").error("rotation mismatch: backup=%s, primary=%s", prev_rotation, current_rotation)
        raise ValueError("rotation mismatch")
    
    new_rotation = current_rotation + 1
    
    token_path, _ = write_token_primary(token, primary_mount)
    _state_save(primary_mount, new_rotation)
    
    # Read the new token's content before writing the backup
    new_token_data = token_path.read_bytes()
    
    # Pass the actual token data to the backup function
    backup_path = write_backup(new_token_data, passphrase, backup_mount, rotation=new_rotation)
    
    return {
        "token": str(token_path),
        "backup": str(backup_path),
        "rotation": new_rotation
    }

def init_dual_usb(token: bytes, primary_mount: Path, backup_mount: Path, passphrase: str) -> dict:
    """Initialize dual USB setup: write token to primary, encrypted backup to backup."""
    from .backup import write_backup
    token_path, meta_path = write_token_primary(token, primary_mount)
    backup_file = write_backup(token, passphrase, backup_mount, rotation=0)
    _state_save(primary_mount, 0)
    return {"primary_token": str(token_path), "primary_meta": str(meta_path), "backup_file": str(backup_file)}

def verify_dual_setup(primary_token_path: Path, backup_file: Path, passphrase: str, enforce_device: bool, enforce_rotation: bool) -> bool:
    """Verify integrity of both primary and backup, and their consistency."""
    from .crypto import verify_backup
    from .backup import _read_backup_meta
    
    token = primary_token_path.read_bytes()
    
    # 1. Verify primary device binding
    if not verify_primary_binding(primary_token_path, enforce=enforce_device):
        _audit("verify_fail_device", {"path": str(primary_token_path)})
        return False
        
    # 2. Verify backup integrity
    if not verify_backup(backup_file, passphrase, token):
        _audit("verify_fail_backup_integrity", {"backup": str(backup_file)})
        return False
        
    # 3. Verify rotation counter consistency
    if enforce_rotation:
        primary_state = _state_load(primary_token_path.parent)
        backup_meta = _read_backup_meta(backup_file)
        if primary_state.get("rotation") != backup_meta.get("rotation"):
            _audit("verify_fail_rotation", {"primary": primary_state.get("rotation"), "backup": backup_meta.get("rotation")})
            return False
            
    _audit("verify_ok", {"primary": str(primary_token_path), "backup": str(backup_file)})
    return True
