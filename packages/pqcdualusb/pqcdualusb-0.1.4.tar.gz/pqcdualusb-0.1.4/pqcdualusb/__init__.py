"""
PQC Dual USB Library
====================

Post-quantum cryptography dual USB backup system.

Features:
- Post-quantum cryptography (Kyber1024 + Dilithium3)
- Dual USB token backup with encryption
- Hardware device binding
- Audit logging with tamper detection
- Power analysis attack countermeasures

Main components:
- PostQuantumCrypto: Core PQC operations
- BackupManager: USB backup operations
- UsbDriveDetector: USB device detection
- SecurityConfig: Security configuration

Usage:
    from pqcdualusb import PostQuantumCrypto, UsbDriveDetector
    
    # Initialize crypto
    crypto = PostQuantumCrypto()
    public_key, secret_key = crypto.generate_kem_keypair()
    
    # Find USB drives
    drives = UsbDriveDetector.get_removable_drives()
    # Use logging for status messages instead of print()
"""

__version__ = "0.1.0"
__author__ = "PQC Dual USB Team"
__license__ = "MIT"

# Main public API exports
from .crypto import PostQuantumCrypto, HybridCrypto, PqcBackend
from .usb import UsbDriveDetector  
from .security import SecurityConfig, SecureMemory, TimingAttackMitigation
from .utils import ProgressReporter, InputValidator

# Convenience imports for most common use cases
__all__ = [
    # Core classes
    "PostQuantumCrypto",
    "HybridCrypto", 
    "PqcBackend",  # Backend enum for checking active backend
    "UsbDriveDetector",
    
    # Security utilities
    "SecurityConfig",
    "SecureMemory",
    "TimingAttackMitigation",
    
    # General utilities
    "ProgressReporter",
    "InputValidator",
    
    # Version info
    "__version__"
]

# Package-level configuration
POWER_ANALYSIS_PROTECTION = True  # Enable by default for security

def get_version():
    """Get the current version of pqcdualusb."""
    return __version__

def get_security_info():
    """Get information about security features and algorithms."""
    return {
        "version": __version__,
        "power_analysis_protection": POWER_ANALYSIS_PROTECTION,
        "pqc_algorithms": {
            "kem": "Kyber1024",
            "signature": "Dilithium3"
        },
        "classical_algorithms": {
            "kdf": "Argon2id",
            "encryption": "AES-256-GCM",
            "hmac": "HMAC-SHA256"
        }
    }
