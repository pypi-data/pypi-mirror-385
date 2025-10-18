"""
USB Drive Detection and Management
==================================

Cross-platform USB drive detection and validation functionality.

Components:
- UsbDriveDetector: Detects removable drives on Windows, Linux, and macOS
- Drive validation: Verifies drives are writable and accessible
- Space calculation: Determines available storage capacity
- Drive integrity checks: Validates drive health and accessibility
"""

import os
import sys
import shutil
import secrets
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


class UsbDriveDetector:
    """
    Cross-platform USB drive detection utility.
    
    Provides methods to detect and validate removable storage devices
    across Windows, Linux, and macOS operating systems.
    """
    
    @staticmethod
    def get_removable_drives() -> List[Path]:
        """
        Detect all removable drives on the system.
        
        Scans for USB drives, SD cards, and other removable storage devices
        currently connected to the system. Works across Windows, Linux, and macOS.
        
        Returns:
            List[Path]: List of removable drive mount points
        """
        drives = []
        
        # Different operating systems, different approaches
        if platform.system() == "Windows":
            drives.extend(UsbDriveDetector._get_windows_removable_drives())
        elif platform.system() == "Linux":
            drives.extend(UsbDriveDetector._get_linux_removable_drives())
        elif platform.system() == "Darwin":  # macOS
            drives.extend(UsbDriveDetector._get_macos_removable_drives())
        
        # Filter out any drives that don't exist
        return [Path(drive) for drive in drives if Path(drive).exists()]
    
    @staticmethod
    def _get_windows_removable_drives() -> List[str]:
        """Get removable drives on Windows using multiple methods."""
        drives = []
        
        try:
            # Method 1: WMI query
            result = subprocess.run([
                "powershell", "-Command",
                "Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | Select-Object -ExpandProperty DeviceID"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        drives.append(line.strip() + "\\")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        try:
            # Method 2: FSUTIL query
            result = subprocess.run([
                "fsutil", "fsinfo", "drives"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Parse drives and check if removable
                import re
                drive_letters = re.findall(r'([A-Z]:)', result.stdout)
                for letter in drive_letters:
                    try:
                        # Skip system drives
                        if letter.upper() not in ['C:', 'D:'] and letter + "\\" not in drives:
                            drives.append(letter + "\\")
                    except Exception:
                        continue
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return drives
    
    @staticmethod
    def _get_linux_removable_drives() -> List[str]:
        """Get removable drives on Linux."""
        drives = []
        
        try:
            # Method 1: lsblk
            result = subprocess.run([
                "lsblk", "-rno", "NAME,TYPE,MOUNTPOINT,HOTPLUG"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 4 and parts[1] == "part" and parts[3] == "1" and len(parts) > 2:
                        mount_point = parts[2]
                        if mount_point != "":
                            drives.append(mount_point)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        try:
            # Method 2: Check /media and /mnt
            media_paths = ["/media", "/mnt", f"/media/{os.getenv('USER', '')}", "/run/media"]
            for media_path in media_paths:
                if os.path.exists(media_path):
                    for item in os.listdir(media_path):
                        full_path = os.path.join(media_path, item)
                        if os.path.ismount(full_path):
                            drives.append(full_path)
        except OSError:
            pass
        
        return list(set(drives))  # Remove duplicates
    
    @staticmethod
    def _get_macos_removable_drives() -> List[str]:
        """Get removable drives on macOS."""
        drives = []
        
        try:
            # Method 1: diskutil to get external devices
            result = subprocess.run([
                "diskutil", "list", "-plist", "external"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse plist output for disk identifiers
                import plistlib
                try:
                    plist_data = plistlib.loads(result.stdout.encode())
                    if 'AllDisksAndPartitions' in plist_data:
                        for disk_entry in plist_data['AllDisksAndPartitions']:
                            if 'Partitions' in disk_entry:
                                for partition in disk_entry['Partitions']:
                                    if 'MountPoint' in partition:
                                        mount_point = partition['MountPoint']
                                        if mount_point and os.path.exists(mount_point):
                                            drives.append(mount_point)
                except (plistlib.InvalidFileException, KeyError):
                    # Fallback to simple text parsing if plist parsing fails
                    pass
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ImportError):
            pass
        
        # Method 2: Check /Volumes for removable devices
        try:
            volumes_path = "/Volumes"
            if os.path.exists(volumes_path):
                for item in os.listdir(volumes_path):
                    full_path = os.path.join(volumes_path, item)
                    if os.path.ismount(full_path) and item not in ["Macintosh HD", "System"]:
                        # Additional check to see if it's removable using diskutil info
                        try:
                            info_result = subprocess.run([
                                "diskutil", "info", full_path
                            ], capture_output=True, text=True, timeout=5)
                            
                            if info_result.returncode == 0:
                                info_text = info_result.stdout.lower()
                                # Look for indicators of removable media
                                if any(indicator in info_text for indicator in [
                                    "removable media:", "yes",
                                    "ejectable:", "yes",
                                    "external:", "yes"
                                ]):
                                    drives.append(full_path)
                            else:
                                # Assume removable if diskutil info fails
                                drives.append(full_path)
                        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                            drives.append(full_path)
        except OSError:
            pass
        
        return list(set(drives))  # Remove duplicates
    
    @staticmethod
    def is_drive_writable(drive_path: Path) -> bool:
        """Test if drive is writable by creating a temporary file."""
        if not drive_path.exists():
            return False
        
        try:
            test_file = drive_path / f".write_test_{secrets.token_hex(8)}"
            test_file.write_bytes(b"test")
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def get_drive_info(drive_path: Path) -> Dict[str, Any]:
        """Get detailed information about a drive."""
        info = {
            "path": str(drive_path),
            "exists": drive_path.exists(),
            "writable": False,
            "free_space": 0,
            "total_space": 0,
            "used_space": 0,
            "filesystem": None,
            "label": None
        }
        
        if info["exists"]:
            info["writable"] = UsbDriveDetector.is_drive_writable(drive_path)
            
            try:
                stat = shutil.disk_usage(drive_path)
                info["free_space"] = stat.free
                info["total_space"] = stat.total
                info["used_space"] = stat.total - stat.free
            except OSError:
                pass
            
            # Try to get filesystem information
            if platform.system() == "Windows":
                info.update(UsbDriveDetector._get_windows_drive_info(drive_path))
            elif platform.system() == "Linux":
                info.update(UsbDriveDetector._get_linux_drive_info(drive_path))
            elif platform.system() == "Darwin":
                info.update(UsbDriveDetector._get_macos_drive_info(drive_path))
        
        return info
    
    @staticmethod
    def _get_windows_drive_info(drive_path: Path) -> Dict[str, Any]:
        """Get Windows-specific drive information."""
        info = {}
        
        try:
            # Get volume information
            result = subprocess.run([
                "powershell", "-Command",
                f"Get-WmiObject -Class Win32_LogicalDisk -Filter \"DeviceID='{drive_path.anchor.rstrip(os.sep)}'\" | Select-Object FileSystem, VolumeName"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "FileSystem" in line and ":" in line:
                        info["filesystem"] = line.split(":")[-1].strip()
                    elif "VolumeName" in line and ":" in line:
                        info["label"] = line.split(":")[-1].strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return info
    
    @staticmethod
    def _get_linux_drive_info(drive_path: Path) -> Dict[str, Any]:
        """Get Linux-specific drive information."""
        info = {}
        
        try:
            # Get filesystem info using df
            result = subprocess.run([
                "df", "-T", str(drive_path)
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) > 1:
                        info["filesystem"] = parts[1]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        try:
            # Get label using lsblk
            result = subprocess.run([
                "lsblk", "-rno", "LABEL", str(drive_path)
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                info["label"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return info
    
    @staticmethod
    def _get_macos_drive_info(drive_path: Path) -> Dict[str, Any]:
        """Get macOS-specific drive information."""
        info = {}
        
        try:
            # Get filesystem info using diskutil
            result = subprocess.run([
                "diskutil", "info", str(drive_path)
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "File System Personality:" in line:
                        info["filesystem"] = line.split(":")[-1].strip()
                    elif "Volume Name:" in line:
                        info["label"] = line.split(":")[-1].strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return info
    
    @staticmethod
    def validate_removable_drive(drive_path: Path) -> Dict[str, Any]:
        """
        Validate that a drive is suitable for use as a removable USB drive.
        
        Returns:
            Dictionary with validation results and any issues found
        """
        validation = {
            "valid": False,
            "issues": [],
            "warnings": [],
            "info": {}
        }
        
        # Get drive information
        drive_info = UsbDriveDetector.get_drive_info(drive_path)
        validation["info"] = drive_info
        
        # Check if drive exists
        if not drive_info["exists"]:
            validation["issues"].append("Drive does not exist")
            return validation
        
        # Check if drive is writable
        if not drive_info["writable"]:
            validation["issues"].append("Drive is not writable")
        
        # Check available space (warn if less than 100MB)
        if drive_info["free_space"] < 100 * 1024 * 1024:
            validation["warnings"].append("Low free space (less than 100MB)")
        
        # Check if it's actually removable (basic heuristic)
        if platform.system() == "Windows":
            drive_letter = str(drive_path).split(':')[0]
            if drive_letter.upper() in ['C', 'D'] and drive_info["total_space"] > 100 * 1024**3:  # >100GB
                validation["warnings"].append("Drive may not be removable (large capacity system drive)")
        
        # If no critical issues, mark as valid
        if not validation["issues"]:
            validation["valid"] = True
        
        return validation
    
    @staticmethod
    def format_drive_size(size_bytes: int) -> str:
        """Format drive size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    @staticmethod
    def list_drives_interactive(output_callback=None, input_callback=None) -> Optional[Path]:
        """
        Interactive drive selection for CLI use.
        
        NOTE: This function is for CLI tools only. Library users should call
        get_removable_drives() directly and implement their own UI.
        
        Args:
            output_callback: Optional callback(message: str) for output
            input_callback: Optional callback(prompt: str) -> str for input
        
        Returns:
            Selected drive path or None if cancelled
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Default to print/input for CLI compatibility
        if output_callback is None:
            def output_callback(msg):
                print(msg)
        
        if input_callback is None:
            def input_callback(prompt):
                return input(prompt)
        
        drives = UsbDriveDetector.get_removable_drives()
        
        if not drives:
            output_callback("No removable drives found.")
            logger.info("No removable drives detected")
            return None
        
        logger.info(f"Found {len(drives)} removable drives")
        output_callback("Available removable drives:")
        
        for i, drive in enumerate(drives, 1):
            info = UsbDriveDetector.get_drive_info(drive)
            size_str = UsbDriveDetector.format_drive_size(info["total_space"])
            free_str = UsbDriveDetector.format_drive_size(info["free_space"])
            label = info.get("label", "Unlabeled")
            filesystem = info.get("filesystem", "Unknown")
            
            output_callback(f"  {i}. {drive} [{label}] ({filesystem}, {size_str}, {free_str} free)")
        
        while True:
            try:
                choice = input_callback("\nSelect drive (1-{}) or 'q' to quit: ".format(len(drives)))
                if choice.lower() == 'q':
                    logger.info("Drive selection cancelled by user")
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(drives):
                    selected = drives[index]
                    logger.info(f"User selected drive: {selected}")
                    return selected
                else:
                    output_callback(f"Please enter a number between 1 and {len(drives)}")
            except (ValueError, KeyboardInterrupt):
                output_callback("\nOperation cancelled.")
                logger.info("Drive selection cancelled")
                return None


def get_drive_selection_info() -> Dict[str, Any]:
    """Get information about available drives for selection."""
    drives = UsbDriveDetector.get_removable_drives()
    
    drive_list = []
    for drive in drives:
        info = UsbDriveDetector.get_drive_info(drive)
        validation = UsbDriveDetector.validate_removable_drive(drive)
        
        drive_list.append({
            "path": str(drive),
            "info": info,
            "validation": validation,
            "formatted_size": UsbDriveDetector.format_drive_size(info["total_space"]),
            "formatted_free": UsbDriveDetector.format_drive_size(info["free_space"])
        })
    
    return {
        "total_drives": len(drives),
        "drives": drive_list,
        "platform": platform.system()
    }
