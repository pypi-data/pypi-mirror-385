# PQC Dual USB Library

[![PyPI version](https://badge.fury.io/py/pqcdualusb.svg)](https://badge.fury.io/py/pqcdualusb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Post-Quantum](https://img.shields.io/badge/Security-Post--Quantum-red.svg)](https://en.wikipedia.org/wiki/Post-quantum_cryptography)

A comprehensive **Python library** for post-quantum cryptographic dual USB backup operations with advanced hardware security features and side-channel attack countermeasures.

> **NOTE:** This is a library package** designed to be imported into your applications. It provides a set of functions to manage secure backups. For the full documentation with interactive diagrams, architecture details, and contribution guidelines, please visit the [GitHub Repository](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library).

---

## Overview

The **PQC Dual USB Library** provides a robust, enterprise-grade solution for securing data against threats from both classical and quantum computers. It offers a functional API for developers to integrate post-quantum cryptography (PQC) into applications requiring secure data storage, especially for scenarios involving redundant backups on physical devices like USB drives.

The library is designed with a "secure-by-default" philosophy, automatically handling complex security operations like side-channel attack mitigation, secure memory management, and hybrid cryptographic schemes.

---

## ️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR APPLICATION                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ Import & Use
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  pqcdualusb Library                         │
├─────────────────────────────────────────────────────────────┤
│  storage.py    │  High-level API (init, rotate, verify)    │
│  backup.py     │  Backup creation and restoration          │
│  crypto.py     │  Classical crypto (AES-256-GCM, Argon2id) │
│  pqc.py        │  Post-quantum crypto (Kyber, Dilithium)   │
│  device.py     │  USB device validation                    │
│  audit.py      │  Tamper-evident logging                   │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Physical Storage (USB Drives)                  │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  PRIMARY USB │              │  BACKUP USB  │            │
│  │  • Token     │◄────────────►│  • Token     │            │
│  │  • State     │   Redundant  │  • State     │            │
│  │  • Backup    │              │  • Backup    │            │
│  └──────────────┘              └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### Post-Quantum Security
-   **NIST-standardized algorithms**: Kyber1024 (KEM) and Dilithium3 (signatures)
-   **Hybrid encryption**: Combines classical AES-256-GCM with post-quantum KEMs
-   **Future-proof**: Protection against both classical and quantum computer attacks

### Dual USB Architecture
-   **Split secret design**: Data is secured across two physical USB devices
-   **Redundant storage**: Automatic synchronization between primary and backup drives
-   **Atomic operations**: Ensures data integrity even during power failures

### ️ Security Features
-   **Secure memory**: Automatic wiping of sensitive data from RAM
-   **Side-channel resistance**: Constant-time operations to prevent timing attacks
-   **Strong KDF**: Argon2id protects passphrases against brute-force attacks
-   **Tamper-evident logging**: Comprehensive audit trail of all security events

### Developer-Friendly
-   **Simple API**: Clean, functional interface with minimal boilerplate
-   **Type hints**: Full type annotations for better IDE support
-   **Comprehensive tests**: Extensive test suite ensures reliability
-   **Cross-platform**: Works on Windows, Linux, and macOS

---

## Installation

```bash
pip install pqcdualusb
```

### Backend Dependencies

The library requires at least one PQC backend. Choose one:

**Option 1: Python backend (Recommended for most users)**
```bash
pip install pqcdualusb[pqc]
```

**Option 2: High-performance Rust backend**

For advanced users who need maximum performance. See the [GitHub README](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library#installation) for Rust setup instructions.

---

## Quick Start Guide

This example demonstrates the end-to-end process of creating and managing a secure dual USB backup using the library's functions.

### Basic Usage

```python
from pathlib import Path
from pqcdualusb.storage import init_dual_usb, rotate_token, verify_dual_setup
from pqcdualusb.backup import restore_from_backup

# Define your USB drive paths
primary_usb = Path("/media/usb1")  # Adjust to your system
backup_usb = Path("/media/usb2")   # Adjust to your system

# Your secret data (e.g., encryption key, master password)
secret_data = b"my-super-secret-master-key"
passphrase = "a-very-strong-and-unique-passphrase"

# 1. Initialize the dual USB backup system
init_info = init_dual_usb(
    token=secret_data,
    primary_mount=primary_usb,
    backup_mount=backup_usb,
    passphrase=passphrase
)
print(f" Initialized: {init_info['primary']}, {init_info['backup']}")

# 2. Verify the backup integrity
is_valid = verify_dual_setup(
    primary_mount=primary_usb,
    backup_mount=backup_usb,
    passphrase=passphrase
)
print(f" Backup verified: {is_valid}")

# 3. Rotate the secret (e.g., periodic key rotation)
new_secret = b"my-new-rotated-master-key"
rotate_info = rotate_token(
    token=new_secret,
    primary_mount=primary_usb,
    backup_mount=backup_usb,
    passphrase=passphrase,
    prev_rotation=0  # Increment on each rotation
)
print(f" Token rotated to rotation #{rotate_info['rotation']}")

# 4. Restore from backup (disaster recovery)
restore_path = Path("/media/usb_restore")
restored_token, _ = restore_from_backup(
    backup_file=Path(rotate_info['backup']),
    restore_primary=restore_path,
    passphrase=passphrase
)
print(f" Restored to: {restored_token}")
```

### Complete Example with Error Handling

```python
import os
from pathlib import Path
import tempfile
import shutil

# Import the necessary functions from the library
from pqcdualusb.storage import init_dual_usb, rotate_token
from pqcdualusb.backup import restore_from_backup
from pqcdualusb.crypto import verify_backup
from pqcdualusb.exceptions import (
    PassphraseMismatchError,
    BackupVerificationError,
    DeviceNotFoundError
)

# --- Setup: Create temporary directories to simulate USB drives ---
# In a real application, these paths would point to your actual USB drives.
tmp_dir = Path(tempfile.mkdtemp(prefix="pqc_usb_demo_"))
primary_path = tmp_dir / "PRIMARY"
backup_path = tmp_dir / "BACKUP"
primary_path.mkdir()
backup_path.mkdir()

print(f" Simulating USB drives:\n   Primary: {primary_path}\n   Backup:  {backup_path}\n")

# --- Core Variables ---
passphrase = "a-very-strong-and-unique-passphrase"
initial_secret = os.urandom(64)  # 512-bit secret

try:
    # 1. Initialize the Dual USB Backup
    print("Step 1: Initializing the dual USB backup...")
    init_info = init_dual_usb(
        token=initial_secret,
        primary_mount=primary_path,
        backup_mount=backup_path,
        passphrase=passphrase
    )
    print(f" Initialization complete.")
    print(f"   Primary: {init_info['primary']}")
    print(f"   Backup:  {init_info['backup']}\n")

    # 2. Verify the Backup Integrity
    print("Step 2: Verifying the backup file...")
    is_valid = verify_backup(
        Path(init_info['backup_file']),
        passphrase,
        initial_secret
    )
    if is_valid:
        print(" Backup integrity verified successfully.\n")
    else:
        raise BackupVerificationError("Backup verification failed!")

    # 3. Rotate the Token with a New Secret
    print("Step 3: Rotating the token with a new secret...")
    new_secret = os.urandom(64)
    rotate_info = rotate_token(
        token=new_secret,
        primary_mount=primary_path,
        backup_mount=backup_path,
        passphrase=passphrase,
        prev_rotation=0
    )
    print(f" Token rotation complete.")
    print(f"   Rotation number: {rotate_info['rotation']}")
    print(f"   New backup: {rotate_info['backup']}\n")

    # 4. Restore from the Latest Backup
    print("Step 4: Restoring the secret from the latest backup...")
    restore_path = tmp_dir / "RESTORED"
    restore_path.mkdir()
    
    restored_token_path, _ = restore_from_backup(
        backup_file=Path(rotate_info['backup']),
        restore_primary=restore_path,
        passphrase=passphrase
    )
    
    # Verify that the restored data matches the new secret
    restored_data = restored_token_path.read_bytes()
    assert restored_data == new_secret, "Restored data doesn't match!"
    print(f" Restore successful!")
    print(f"   Restored to: {restored_token_path}")
    print(f"   Data verified: {len(restored_data)} bytes match.\n")

except PassphraseMismatchError:
    print(" Error: Incorrect passphrase provided.")
except BackupVerificationError as e:
    print(f" Error: Backup verification failed - {e}")
except DeviceNotFoundError as e:
    print(f" Error: USB device not found - {e}")
except Exception as e:
    print(f" Unexpected error: {e}")
finally:
    # --- Cleanup ---
    shutil.rmtree(tmp_dir)
    print(" Cleanup complete.")
```

---

## Security Properties

### Cryptographic Stack

| Component | Algorithm | Purpose |
|-----------|-----------|---------|
| **Key Derivation** | Argon2id | Protects passphrase from brute-force attacks |
| **Symmetric Encryption** | AES-256-GCM | Fast, authenticated encryption for data |
| **Post-Quantum KEM** | Kyber1024 | Quantum-resistant key encapsulation |
| **Post-Quantum Signature** | Dilithium3 | Quantum-resistant digital signatures |
| **HMAC** | HMAC-SHA256 | Additional integrity verification |

### Security Workflow

```
User Passphrase
      │
      ▼
┌─────────────┐
│  Argon2id   │  ← Memory-hard KDF
└──────┬──────┘
       │
       ▼
  Master Key (256-bit)
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ AES-256-GCM  │      │  Kyber1024   │
│  Classical   │      │ Post-Quantum │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
          Encrypted Secret
                  │
                  ▼
┌─────────────────────────────┐
│       Dilithium3            │
│   Digital Signature         │
└─────────────────────────────┘
                  │
                  ▼
        USB Storage (Dual)
```

---

## API Reference

### Core Functions

#### `init_dual_usb(token, primary_mount, backup_mount, passphrase)`
Initialize a new dual USB backup system.

**Parameters:**
- `token` (bytes): The secret data to protect (32-128 bytes recommended)
- `primary_mount` (Path): Path to the primary USB drive
- `backup_mount` (Path): Path to the backup USB drive
- `passphrase` (str): User passphrase for encryption

**Returns:** Dictionary with initialization information

---

#### `rotate_token(token, primary_mount, backup_mount, passphrase, prev_rotation)`
Rotate the secret with a new value.

**Parameters:**
- `token` (bytes): The new secret data
- `primary_mount` (Path): Path to the primary USB drive
- `backup_mount` (Path): Path to the backup USB drive
- `passphrase` (str): User passphrase (must match initialization)
- `prev_rotation` (int): Previous rotation number

**Returns:** Dictionary with rotation information

---

#### `verify_dual_setup(primary_mount, backup_mount, passphrase)`
Verify the integrity of the dual USB setup.

**Parameters:**
- `primary_mount` (Path): Path to the primary USB drive
- `backup_mount` (Path): Path to the backup USB drive  
- `passphrase` (str): User passphrase

**Returns:** `True` if verification passes, `False` otherwise

---

#### `restore_from_backup(backup_file, restore_primary, passphrase)`
Restore data from a backup file.

**Parameters:**
- `backup_file` (Path): Path to the backup file
- `restore_primary` (Path): Path where to restore the primary token
- `passphrase` (str): User passphrase

**Returns:** Tuple of (restored_token_path, state_data)

---

## Use Cases

### 1. **Cryptocurrency Wallet Protection**
Securely store master private keys across two USB devices with quantum-resistant encryption.

### 2. **Enterprise Key Management**
Manage encryption keys for organizational data with audit logging and rotation capabilities.

### 3. **Password Manager Master Key**
Protect the master encryption key for password management systems with redundant backups.

### 4. **Secure Document Storage**
Encrypt and backup sensitive documents with post-quantum security guarantees.

### 5. **Hardware Security Module (HSM) Backup**
Create offline backups of HSM keys with tamper-evident logging.

---

## Advanced Configuration

### Custom Argon2id Parameters

```python
from pqcdualusb.crypto import derive_key

# High-security settings (slower but more secure)
key = derive_key(
    passphrase="my-passphrase",
    salt=b"random-salt-32-bytes",
    time_cost=4,      # Default: 3
    memory_cost=65536 # Default: 65536 (64 MB)
)
```

### Secure Memory Wiping

```python
from pqcdualusb.crypto import secure_wipe

sensitive_data = bytearray(b"secret-data")
# Use the data...
secure_wipe(sensitive_data)  # Automatically wipes on deletion
```

---

## Documentation

For comprehensive documentation including:
- **Architecture diagrams** (interactive Mermaid diagrams on GitHub)
- **Detailed API reference**
- **Security analysis**
- **Contribution guidelines**
- **Threat model**

Visit the [GitHub Repository](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library).

---

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/blob/master/CONTRIBUTING.md) file for guidelines.

---

## Security

For security vulnerabilities, please email **Johnsonajibi@gmail.com** instead of using the issue tracker.

See [SECURITY.md](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/blob/master/SECURITY.md) for our security policy.

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/blob/master/LICENSE) file for details.

---

## Acknowledgments

- **NIST** for standardizing post-quantum cryptography algorithms
- **Open Quantum Safe (OQS)** project for the `liboqs` library
- The cryptography community for ongoing research and development

---

## Support

- **Documentation**: [GitHub Repository](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library)
- **Issues**: [GitHub Issues](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/issues)
- **Email**: Johnsonajibi@gmail.com
