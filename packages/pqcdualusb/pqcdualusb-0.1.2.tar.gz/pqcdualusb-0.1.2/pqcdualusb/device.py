"""
device.py
==============================================
Device identification and removable media checks.
"""
from __future__ import annotations

import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional

DeviceId = Dict[str, Optional[str]]

def _device_id_for_path(path: Path) -> DeviceId:
    """Best-effort device identity for filesystem that contains `path`. Never raises."""
    try:
        system = platform.system()
        if system == "Windows":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            GetVolumePathNameW = kernel32.GetVolumePathNameW
            GetVolumeInformationW = kernel32.GetVolumeInformationW
            buf = ctypes.create_unicode_buffer(260)
            GetVolumePathNameW(str(path), buf, 260)
            root = buf.value or str(getattr(path, "drive", path))
            vol_name_buf = ctypes.create_unicode_buffer(261)
            fs_name_buf = ctypes.create_unicode_buffer(261)
            ser_num = ctypes.c_uint()
            max_comp_len = ctypes.c_uint()
            fs_flags = ctypes.c_uint()
            ok = GetVolumeInformationW(ctypes.c_wchar_p(root), vol_name_buf, 260, ctypes.byref(ser_num), ctypes.byref(max_comp_len), ctypes.byref(fs_flags), fs_name_buf, 260)
            return {"uuid": f"{ser_num.value:08X}" if ok else None, "label": vol_name_buf.value if ok else None, "fs": fs_name_buf.value if ok else None, "model": None}
        elif system == "Darwin":
            try:
                mp = Path(subprocess.check_output(["/bin/df", "-P", str(path)], text=True).splitlines()[-1].split()[5])
            except Exception:
                mp = Path("/")
            try:
                out = subprocess.check_output(["/usr/sbin/diskutil", "info", str(mp)], text=True)
                uuid = label = model = fs = None
                for line in out.splitlines():
                    if "Volume UUID:" in line: uuid = line.split(":", 1)[1].strip()
                    if "Volume Name:" in line: label = line.split(":", 1)[1].strip()
                    if "Device / Media Name:" in line: model = line.split(":", 1)[1].strip()
                    if "Type (Bundle):" in line: fs = line.split(":", 1)[1].strip()
                return {"uuid": uuid, "label": label, "fs": fs, "model": model}
            except Exception:
                return {"uuid": None, "label": None, "fs": None, "model": None}
        else:
            device = None
            best_mnt = ""
            try:
                with open("/proc/mounts", "r", encoding="utf-8") as f:
                    for line in f:
                        dev, mnt, *_ = line.split()
                        try:
                            p = Path(path).resolve()
                            m = Path(mnt)
                            if str(p).startswith(str(m.resolve())) and len(str(m)) > len(best_mnt):
                                best_mnt = str(m)
                                device = dev
                        except Exception:
                            continue
                if not device:
                    return {"uuid": None, "label": None, "fs": None, "model": None}
                blkid_path = shutil.which("blkid") or "/sbin/blkid"
                out = subprocess.check_output([blkid_path, "-o", "export", device], stderr=subprocess.DEVNULL, text=True)
                kv = dict(line.strip().split("=", 1) for line in out.strip().splitlines() if "=" in line)
                return {"uuid": kv.get("UUID"), "label": kv.get("LABEL"), "fs": kv.get("TYPE"), "model": kv.get("MODEL")}
            except Exception:
                return {"uuid": None, "label": None, "fs": None, "model": None}
    except Exception:
        return {"uuid": None, "label": None, "fs": None, "model": None}

def _is_removable_path(path: Path) -> bool:
    try:
        system = platform.system()
        if system == "Windows":
            import ctypes
            DRIVE_REMOVABLE = 2
            drive = str(getattr(path, "drive", path))
            dtype = ctypes.windll.kernel32.GetDriveTypeW(drive)
            if dtype == DRIVE_REMOVABLE:
                if str(drive).upper().startswith(("A:", "B:")):
                    return False
                di = _device_id_for_path(path)
                fs = (di.get("fs") or "").lower()
                return fs in {"fat", "fat32", "exfat", "ntfs", "refs"}
            return False
        elif system == "Darwin":
            try:
                mp = Path(subprocess.check_output(["/bin/df", "-P", str(path)], text=True).splitlines()[-1].split()[5])
            except Exception:
                mp = Path("/")
            try:
                out = subprocess.check_output(["/usr/sbin/diskutil", "info", str(mp)], text=True)
                is_ext = any(("Device Location: External" in line) or ("Removable Media: Yes" in line) for line in out.splitlines())
                return bool(is_ext)
            except Exception:
                return False
        else:
            device = None
            best_mnt = ""
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    dev, mnt, *_ = line.split()
                    p = Path(path).resolve(); m = Path(mnt)
                    try:
                        if str(p).startswith(str(m.resolve())) and len(str(m)) > len(best_mnt):
                            best_mnt = str(m); device = dev
                    except Exception:
                        continue
            if not device or not device.startswith("/dev/"):
                return False
            base = os.path.basename(device)
            cand = [f"/sys/block/{base}/removable", f"/sys/block/{base.rstrip('0123456789')}/removable"]
            for c in cand:
                try:
                    with open(c, "r", encoding="utf-8") as fh:
                        return fh.read().strip() == "1"
                except Exception:
                    continue
            return False
    except Exception:
        return False

def list_usb_drives(show_details: bool = False) -> None:
    """List available USB drives with optional detailed information."""
    from .usb import UsbDriveDetector
    drives = UsbDriveDetector.get_removable_drives()
    if not drives:
        print("No removable USB drives detected.")
        return
    
    print(f"Found {len(drives)} removable drive(s):")
    for i, drive in enumerate(drives, 1):
        if show_details:
            info = UsbDriveDetector.get_drive_info(drive)
            free_gb = info['free_space'] / (1024**3) if info['free_space'] > 0 else 0
            total_gb = info['total_space'] / (1024**3) if info['total_space'] > 0 else 0
            writable_status = "✓" if info['writable'] else "✗"
            print(f"  {i}. {drive}")
            print(f"     Writable: {writable_status}")
            print(f"     Space: {free_gb:.1f} GB free / {total_gb:.1f} GB total")
        else:
            print(f"  {i}. {drive}")

def select_usb_drive(prompt: str, exclude: Optional[Path] = None) -> Path:
    """Interactively select a USB drive from available options."""
    from .usb import UsbDriveDetector
    from .exceptions import CliUsageError
    import sys
    drives = UsbDriveDetector.get_removable_drives()
    
    if exclude:
        drives = [d for d in drives if d != exclude]
    
    if not drives:
        if exclude:
            raise CliUsageError(1, "No other removable USB drives available.")
        else:
            raise CliUsageError(1, "No removable USB drives detected.")
    
    if len(drives) == 1:
        print(f"Auto-selecting only available drive: {drives[0]}")
        return drives[0]
    
    print(f"\n{prompt}")
    list_usb_drives(show_details=True)
    
    while True:
        try:
            choice = input(f"\nSelect drive (1-{len(drives)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(drives):
                return drives[index]
            else:
                print(f"Please enter a number between 1 and {len(drives)}")
        except (ValueError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            sys.exit(1)
