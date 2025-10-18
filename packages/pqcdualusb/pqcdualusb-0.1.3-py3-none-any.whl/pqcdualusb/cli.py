"""
cli.py
==============================================
Command-line interface for the application.
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .security import InputValidator
from .storage import init_dual_usb, rotate_token, verify_dual_setup
from .backup import restore_from_backup
from .pqc import pq_write_audit_keys, pq_enable_audit_signing, HAS_OQS
from .device import list_usb_drives, _is_removable_path, _device_id_for_path
from .audit import verify_audit_log
from .utils import ProgressReporter

class CliUsageError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code

def _read_pass(args) -> str:
    if getattr(args, "passphrase_env", None):
        val = os.getenv(args.passphrase_env)
        if not val:
            raise CliUsageError(2, f"Environment variable {args.passphrase_env} is empty")
        return val
    if getattr(args, "passphrase", None):
        return args.passphrase
    return getpass.getpass("Passphrase: ")

def _ensure_removable_and_distinct(primary: Path, backup: Path) -> None:
    try:
        p_res = primary.resolve(strict=False)
        b_res = backup.resolve(strict=False)
    except Exception:
        p_res, b_res = primary, backup
    if p_res == b_res:
        raise CliUsageError(5, "Primary and backup paths must be different")
    pid = _device_id_for_path(primary); bid = _device_id_for_path(backup)
    if pid.get("uuid") and bid.get("uuid") and pid.get("uuid") == bid.get("uuid"):
        raise CliUsageError(6, "Primary and backup appear to be the same device (matching UUID)")
    if not _is_removable_path(primary):
        raise CliUsageError(7, "Primary path does not appear to be a removable device")
    if not _is_removable_path(backup):
        raise CliUsageError(8, "Backup path does not appear to be a removable device")

def _cmd_init(args):
    try:
        primary = InputValidator.validate_path(args.primary, must_exist=True, must_be_dir=True)
        backup = InputValidator.validate_path(args.backup, must_exist=True, must_be_dir=True)
        size = InputValidator.validate_token_size(args.random or 64)
        
        pw = _read_pass(args)
        pw = InputValidator.validate_passphrase(pw)
        
        token = os.urandom(size)
        _ensure_removable_and_distinct(primary, backup)
        
        progress = ProgressReporter(description="Initializing dual USB setup")
        progress.set_total(100)
        
        progress.update(50)
        info = init_dual_usb(token, primary, backup, pw)
        progress.update(50)
        progress.finish()
        
        print(info)
        
        __import__("pqcdualusb.security").secure_zero_memory(bytearray(token))
        __import__("pqcdualusb.security").secure_zero_memory(bytearray(pw.encode()))
        
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

def _cmd_rotate(args):
    try:
        primary = InputValidator.validate_path(args.primary, must_exist=True, must_be_dir=True)
        backup = InputValidator.validate_path(args.backup, must_exist=True, must_be_dir=True)
        size = InputValidator.validate_token_size(args.random or 64)
        
        pw = _read_pass(args)
        pw = InputValidator.validate_passphrase(pw)
        
        token = os.urandom(size)
        _ensure_removable_and_distinct(primary, backup)
        
        progress = ProgressReporter(description="Rotating token")
        progress.set_total(100)
        
        progress.update(50)
        info = rotate_token(token, primary, backup, pw, args.prev_rotation)
        progress.update(50)
        progress.finish()
        
        print(info)
        
        __import__("pqcdualusb.security").secure_zero_memory(bytearray(token))
        __import__("pqcdualusb.security").secure_zero_memory(bytearray(pw.encode()))
        
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def _cmd_verify(args):
    try:
        pw = _read_pass(args)
        primary = Path(args.primary)
        matches = sorted(primary.glob(args.primary_token_name))
        if not matches:
            raise CliUsageError(3, f"No primary token matches pattern {args.primary_token_name} in {primary}")
        primary_token = matches[-1]
        ok = verify_dual_setup(primary_token, Path(args.backup_file), pw, enforce_device=args.enforce_device, enforce_rotation=not args.no_enforce_rotation)
        print("OK" if ok else "FAIL")
        if args.pq_audit_pk:
            pk_path = Path(args.pq_audit_pk)
            aok = verify_audit_log(pk_path)
            print("AUDIT_OK" if aok else "AUDIT_FAIL")
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)

def _cmd_restore(args):
    try:
        pw = _read_pass(args)
        token_path, meta_path = restore_from_backup(Path(args.backup_file), Path(args.restore_primary), pw)
        print({"primary": str(token_path), "meta": str(meta_path)})
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)

def _cmd_pq_init_audit(args):
    try:
        if not HAS_OQS:
            raise CliUsageError(4, "python-oqs not available; install python-oqs to use PQ features")
        pw = _read_pass(args)
        primary = Path(args.primary); backup = Path(args.backup)
        _ensure_removable_and_distinct(primary, backup)
        info = pq_write_audit_keys(primary, backup, pw, level=args.level)
        print(info)
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)

def _cmd_pq_enable_audit(args):
    try:
        if not HAS_OQS:
            raise CliUsageError(4, "python-oqs not available; install python-oqs to use PQ features")
        pq_enable_audit_signing(Path(args.sk_path), level=args.level)
        print({"pq_audit_enabled": True, "level": args.level, "sk_path": args.sk_path})
    except CliUsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)

def _cmd_list_drives(args):
    """Command to list available USB drives."""
    try:
        list_usb_drives(show_details=args.details)
    except Exception as e:
        print(f"Error listing drives: {e}", file=sys.stderr)
        sys.exit(1)

def cli(argv=None):
    p = argparse.ArgumentParser(prog="pqc-dualusb", description="Dual USB Token + Encrypted Backup (USB-only)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("init", help="Initialize with random token")
    a.add_argument("--primary", required=True)
    a.add_argument("--backup", required=True)
    a.add_argument("--random", type=int, default=64)
    a.add_argument("--passphrase-env", dest="passphrase_env")
    a.add_argument("--passphrase")
    a.set_defaults(func=_cmd_init)

    r = sub.add_parser("rotate", help="Rotate with new random token")
    r.add_argument("--primary", required=True)
    r.add_argument("--backup", required=True)
    r.add_argument("--random", type=int, default=64)
    r.add_argument("--prev-rotation", type=int, default=0)
    r.add_argument("--passphrase-env", dest="passphrase_env")
    r.add_argument("--passphrase")
    r.set_defaults(func=_cmd_rotate)

    v = sub.add_parser("verify", help="Verify device binding, rotation, and backup integrity")
    v.add_argument("--primary", required=True)
    v.add_argument("--backup-file", required=True)
    v.add_argument("--primary-token-name", default="token_*.bin")
    v.add_argument("--enforce-device", action="store_true")
    v.add_argument("--no-enforce-rotation", action="store_true")
    v.add_argument("--pq-audit-pk", dest="pq_audit_pk")
    v.add_argument("--passphrase-env", dest="passphrase_env")
    v.add_argument("--passphrase")
    v.set_defaults(func=_cmd_verify)

    d = sub.add_parser("restore", help="Restore a token onto new primary USB from backup file")
    d.add_argument("--backup-file", required=True)
    d.add_argument("--restore-primary", required=True)
    d.add_argument("--passphrase-env", dest="passphrase_env")
    d.add_argument("--passphrase")
    d.set_defaults(func=_cmd_restore)

    pq = sub.add_parser("pq-init-audit", help="Generate Dilithium keys for audit signing and back them up encrypted")
    pq.add_argument("--primary", required=True)
    pq.add_argument("--backup", required=True)
    pq.add_argument("--level", default="Dilithium3", choices=["Dilithium2", "Dilithium3", "Dilithium5"])
    pq.add_argument("--passphrase-env", dest="passphrase_env")
    pq.add_argument("--passphrase")
    pq.set_defaults(func=_cmd_pq_init_audit)

    pqa = sub.add_parser("pq-enable-audit", help="Enable PQ audit signing using an existing secret key on the primary USB")
    pqa.add_argument("--sk-path", required=True)
    pqa.add_argument("--level", default="Dilithium3", choices=["Dilithium2", "Dilithium3", "Dilithium5"])
    pqa.set_defaults(func=_cmd_pq_enable_audit)

    lst = sub.add_parser("list-drives", help="List available removable USB drives")
    lst.add_argument("--details", action="store_true", help="Show detailed drive information")
    lst.set_defaults(func=_cmd_list_drives)

    args = p.parse_args(argv)
    return args.func(args)
