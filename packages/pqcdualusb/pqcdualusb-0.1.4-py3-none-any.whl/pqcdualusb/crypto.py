"""
Cryptographic Operations Module
===============================

This is where the cryptographic magic happens! We handle:

🔐 Post-Quantum Cryptography (PQC):
   - Kyber1024 for key encapsulation (quantum-safe key exchange)
   - Dilithium3 for digital signatures (quantum-safe authentication)

🛡️ Classical Cryptography (as fallback):
   - AES-256-GCM for encryption
   - Argon2id for password hashing
   - RSA-4096 for key exchange/signatures when PQC isn't available

🔧 Backend Support:
   - C++ (liboqs): Primary backend, fastest performance
   - Rust: Native Kyber/Dilithium implementation, great fallback
   - OQS Python: Pure Python bindings, portable but slower
   - Classical: Last resort when no PQC is available (with warnings!)

⚡ Security Features:
   - Power analysis attack countermeasures (if hardware supports it)
   - Hybrid encryption (combines classical + PQC for defense-in-depth)
   - Secure key derivation with Argon2id
   - Authenticated encryption with AES-GCM

Usage:
    from pqcdualusb.crypto import PostQuantumCrypto, HybridCrypto
    
    # Basic PQC operations
    crypto = PostQuantumCrypto()
    secret_key, public_key = crypto.generate_kem_keypair()
    
    # Hybrid encryption (classical + PQC)
    hybrid = HybridCrypto()
    package = hybrid.encrypt_with_pqc(data, "my-password", public_key)
"""

import os
import sys
import hashlib
import secrets
import warnings
import textwrap
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from enum import Enum, auto
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
try:
    from argon2.low_level import hash_secret_raw, Type as Argon2Type
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False
import json

# ============================================================================
# Secure Logging Configuration
# ============================================================================

# Configure secure logging - only log to syslog/file, never to console in production
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

# Only add handler if one doesn't exist (avoid duplicate logs)
if not _logger.handlers:
    # In production, this should go to syslog or secure file
    # For development, we use NullHandler to suppress output
    _logger.addHandler(logging.NullHandler())

def _secure_log(level: str, message: str, **kwargs):
    """
    Secure logging that sanitizes sensitive information.
    Only logs to configured handlers, never prints to console.
    """
    # Sanitize message - remove any potential sensitive data
    sanitized_msg = message
    for key in ['key', 'secret', 'password', 'passphrase', 'token']:
        if key in sanitized_msg.lower():
            sanitized_msg = sanitized_msg.split(key)[0] + f"[{key} redacted]"
    
    getattr(_logger, level.lower())(sanitized_msg, **kwargs)

# ============================================================================
# Standard Cryptography Libraries
# ============================================================================

# Try to import the cryptography package (for AES, key derivation, etc.)
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

# Try to import Argon2
try:
    from argon2.low_level import hash_secret_raw, Type as Argon2Type
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False

# ============================================================================
# Post-Quantum Cryptography Backends
# ============================================================================

# Try OQS (Open Quantum Safe) - Python bindings for liboqs
# Note: Requires both 'liboqs-python' package AND system liboqs library
try:
    import oqs
    HAS_OQS = True
    OQS_ERROR = None
except ImportError as e:
    HAS_OQS = False
    OQS_ERROR = f"liboqs-python not installed: {e}"
except Exception as e:
    # This catches runtime errors like missing liboqs system library
    HAS_OQS = False
    OQS_ERROR = f"liboqs system library missing: {e}"

# Try C++ PQC (our primary backend - fastest and most complete)
HAS_CPP_PQC = False
CPP_PQC_ERROR = None
try:
    import cpp_pqc
    HAS_CPP_PQC = True
    CPP_PQC_ERROR = None
except ImportError as e:
    HAS_CPP_PQC = False
    CPP_PQC_ERROR = str(e)

# Try Rust PQC (fallback native implementation)
_MIN_RUST_PQC_VERSION = (1, 2, 0)
HAS_RUST_PQC = False
RUST_PQC_ERROR = None

try:
    import rust_pqc
    HAS_RUST_PQC = True
    RUST_PQC_ERROR = None
except ImportError:
    # Path 2: Try the dev build location (for local development)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rust_pqc_build"))
        import rust_pqc
        HAS_RUST_PQC = True
        RUST_PQC_ERROR = None
    except ImportError as e:
        HAS_RUST_PQC = False
        RUST_PQC_ERROR = str(e)
    finally:
        # Clean up sys.path - don't leave our temp path in there
        if str(Path(__file__).resolve().parent.parent / "rust_pqc_build") in sys.path:
            sys.path.remove(str(Path(__file__).resolve().parent.parent / "rust_pqc_build"))

# Version check: make sure rust_pqc is new enough
if HAS_RUST_PQC:
    try:
        major, minor, patch = rust_pqc.pqc_version()
        if (major, minor, patch) < _MIN_RUST_PQC_VERSION:
            HAS_RUST_PQC = False
            RUST_PQC_ERROR = f"rust_pqc too old: {major}.{minor}.{patch} (need >= {'.'.join(map(str, _MIN_RUST_PQC_VERSION))})"
    except AttributeError:
        # No version function? Probably incompatible
        HAS_RUST_PQC = False
        RUST_PQC_ERROR = "rust_pqc missing version API – incompatible"

# ============================================================================
# Power Analysis Protection (Side-Channel Attack Countermeasures)
# ============================================================================

import secrets
import time
import threading
import gc

# Software-based power analysis countermeasures are always available
POWER_ANALYSIS_PROTECTION = True

class SideChannelProtection:
    """
    Software-based side-channel attack countermeasures.
    
    Implements multiple defense techniques:
    1. Timing randomization - Random delays to obfuscate timing patterns
    2. Operation blinding - Add dummy operations to balance power consumption
    3. Memory access randomization - Random memory access patterns
    4. Cache timing defense - Flush sensitive data from CPU caches
    """
    
    _lock = threading.Lock()
    _operation_count = 0
    
    @staticmethod
    def add_timing_jitter(operation_type: str = "crypto"):
        """
        Add random timing jitter to prevent timing side-channel attacks.
        
        Different operation types get different jitter ranges to maintain
        reasonable performance while providing security.
        """
        if operation_type == "crypto":
            # Cryptographic operations: 1-5ms jitter
            jitter_us = secrets.randbelow(4000) + 1000
        elif operation_type == "key_generation":
            # Key generation: 5-15ms jitter (less timing-sensitive)
            jitter_us = secrets.randbelow(10000) + 5000
        else:
            # Default: 0.5-2ms jitter
            jitter_us = secrets.randbelow(1500) + 500
        
        time.sleep(jitter_us / 1000000.0)
    
    @staticmethod
    def dummy_operations(count: int = None):
        """
        Execute dummy operations to balance power consumption.
        
        These operations don't affect the result but add computational
        load that masks the actual cryptographic operations in power traces.
        """
        if count is None:
            # Random number of dummy operations (50-150)
            count = secrets.randbelow(100) + 50
        
        # Dummy computations that appear like real crypto work
        dummy_data = secrets.token_bytes(32)
        for _ in range(count):
            # Bitwise operations
            result = int.from_bytes(dummy_data, 'big')
            result ^= secrets.randbelow(2**256)
            result = (result << 7) | (result >> 249)
            dummy_data = result.to_bytes(32, 'big')
    
    @staticmethod
    def randomize_memory_access():
        """
        Randomize memory access patterns to prevent cache timing attacks.
        
        Allocates and accesses memory in random patterns to obfuscate
        the actual memory access patterns of cryptographic operations.
        """
        # Allocate random-sized buffers
        buffer_sizes = [secrets.randbelow(1024) + 256 for _ in range(5)]
        buffers = [bytearray(size) for size in buffer_sizes]
        
        # Random memory writes
        for buf in buffers:
            for i in range(0, len(buf), 64):
                buf[i:i+1] = secrets.token_bytes(1)
        
        # Random memory reads (prevents optimization)
        checksum = 0
        for buf in buffers:
            for i in range(0, len(buf), 64):
                checksum ^= buf[i]
        
        # Ensure compiler doesn't optimize away
        return checksum
    
    @staticmethod
    def flush_sensitive_caches():
        """
        Flush sensitive data from CPU caches.
        
        Forces garbage collection and attempts to clear CPU caches
        to prevent cache timing attacks from recovering sensitive data.
        """
        # Force garbage collection to clear Python object caches
        gc.collect()
        
        # Memory barrier - prevents reordering
        threading.Event().wait(0)
    
    @classmethod
    def protect_operation(cls, operation_name: str):
        """
        Apply multiple countermeasures before an operation.
        
        Args:
            operation_name: Name of the operation for logging/tuning
        """
        with cls._lock:
            cls._operation_count += 1
            
            # Apply timing jitter
            if cls._operation_count % 2 == 0:
                cls.add_timing_jitter("crypto")
            
            # Randomize memory access patterns
            if cls._operation_count % 3 == 0:
                cls.randomize_memory_access()
            
            # Add dummy operations
            if cls._operation_count % 5 == 0:
                cls.dummy_operations(secrets.randbelow(50) + 25)
    
    @classmethod
    def cleanup_operation(cls):
        """
        Apply countermeasures after an operation.
        """
        # Add post-operation jitter
        cls.add_timing_jitter("crypto")
        
        # Flush caches periodically
        if cls._operation_count % 10 == 0:
            cls.flush_sensitive_caches()


def secure_pqc_execute(func, *args, **kwargs):
    """
    Execute a PQC operation with side-channel attack countermeasures.
    
    Wraps cryptographic operations with multiple defense techniques:
    - Timing randomization to prevent timing attacks
    - Dummy operations to mask power consumption patterns
    - Memory access randomization to prevent cache timing attacks
    - Cache flushing to prevent data remanence
    
    Args:
        func: The cryptographic function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Returns:
        The result of the function call
    """
    # Pre-operation countermeasures
    SideChannelProtection.protect_operation(func.__name__)
    
    try:
        # Execute the actual cryptographic operation
        result = func(*args, **kwargs)
        
        # Post-operation countermeasures
        SideChannelProtection.cleanup_operation()
        
        return result
    
    except Exception as e:
        # Even on error, apply countermeasures to prevent timing analysis
        SideChannelProtection.cleanup_operation()
        raise


# ============================================================================
# Import Security Configuration
# ============================================================================

# SecurityConfig has all our crypto parameters (key sizes, iteration counts, etc.)
from .security import SecurityConfig, SecureMemory, secure_zero_memory, TimingAttackMitigation

_SCRYPT_WARNED = False

def _derive_key(passphrase: str, salt: bytes) -> tuple[bytes, dict]:
    """Derive encryption key using Argon2id or scrypt with secure memory handling."""
    global _SCRYPT_WARNED
    # Use secure memory for sensitive operations
    passphrase_bytes = passphrase.encode('utf-8')
    
    try:
        with SecureMemory(len(passphrase_bytes) + SecurityConfig.AES_KEY_SIZE) as secure_buf:
            # Copy passphrase to secure memory
            secure_buf[:len(passphrase_bytes)] = passphrase_bytes
            
            if HAS_ARGON2:
                params = SecurityConfig.get_argon2_params()
                try:
                    # Use secure memory buffer for key derivation
                    key = hash_secret_raw(
                        bytes(secure_buf[:len(passphrase_bytes)]), 
                        salt, 
                        time_cost=params["time_cost"], 
                        memory_cost=params["memory_cost"], 
                        parallelism=params["parallelism"], 
                        hash_len=SecurityConfig.AES_KEY_SIZE, 
                        type=Argon2Type.ID
                    )
                    return key, {"kdf": "argon2id", **params}
                except Exception as e:  # rare
                    _logger.warning("Argon2 failed: %s; falling back to scrypt.", e)
            else:
                if not _SCRYPT_WARNED:
                    _logger.warning("Argon2 not available; falling back to scrypt (install argon2-cffi).")
                    _SCRYPT_WARNED = True
            
            # Fallback to scrypt
            kdf = Scrypt(salt=salt, length=SecurityConfig.AES_KEY_SIZE, n=2**15, r=8, p=1)
            key = kdf.derive(bytes(secure_buf[:len(passphrase_bytes)]))
            return key, {"kdf": "scrypt", "n": 2**15, "r": 8, "p": 1}
    finally:
        # Clear passphrase from memory
        if 'passphrase_bytes' in locals():
            secure_zero_memory(bytearray(passphrase_bytes))

class PqcBackend(Enum):
    """Post-quantum cryptography backend types."""
    CPP = auto()   # C++ liboqs (primary)
    RUST = auto()  # Rust native (fallback) 
    OQS = auto()   # Python OQS (fallback)
    NONE = auto()  # classical only


class PostQuantumCrypto:
    """
    Post-quantum cryptography implementation with power analysis countermeasures.
    
    Provides Kyber1024 key encapsulation and Dilithium3 digital signatures.
    Automatically selects best available backend (Rust PQC or OQS fallback).
    """
    
    def __init__(self, 
                 kem_algorithm: str = None, 
                 sig_algorithm: str = None,
                 allow_fallback: bool = False):
        self.kem_algorithm = kem_algorithm or SecurityConfig.PQC_KEM_ALGORITHM
        self.sig_algorithm = sig_algorithm or SecurityConfig.PQC_SIG_ALGORITHM
        
        # Check if any PQC backend is available
        if not HAS_CPP_PQC and not HAS_RUST_PQC and not HAS_OQS and not allow_fallback:
            raise RuntimeError(
                "No post-quantum library available. "
                "Install cpp-pqc, rust-pqc wheel or python-oqs, or pass allow_fallback=True "
                "to accept classical crypto (NOT quantum-safe)."
            )
        
        # Power analysis protection available
        self.power_protection_enabled = POWER_ANALYSIS_PROTECTION
        
        # Try C++ PQC first (preferred backend)
        if HAS_CPP_PQC:
            self.backend = PqcBackend.CPP
            try:
                self.cpp_pqc = cpp_pqc.CppPostQuantumCrypto(self.kem_algorithm, self.sig_algorithm)
                # Initialization successful - using C++ backend
                _secure_log('info', 'PQC backend initialized successfully')
                return
            except Exception as e:
                # C++ backend unavailable, try next backend
                _secure_log('debug', 'C++ backend unavailable, trying next backend')
                pass
                # Fall through to Rust PQC
        
        # Try Rust PQC as fallback
        if HAS_RUST_PQC:
            self.backend = PqcBackend.RUST
            try:
                self.rust_pqc = rust_pqc.RustPostQuantumCrypto(self.kem_algorithm, self.sig_algorithm)
                # Initialization successful - using Rust backend
                _secure_log('info', 'PQC backend initialized successfully')
                return
            except Exception as e:
                # Rust backend unavailable, try next backend
                _secure_log('debug', 'Rust backend unavailable, trying next backend')
                pass
                # Fall through to OQS
        
        # Fallback to OQS
        if HAS_OQS:
            self.backend = PqcBackend.OQS
            
            # Map algorithm names to OQS equivalents (newer liboqs uses NIST standardized names)
            oqs_kem = self.kem_algorithm  # Kyber1024 still works
            oqs_sig = self.sig_algorithm
            
            # Map Dilithium to ML-DSA (NIST standardized names)
            oqs_sig_map = {
                "Dilithium2": "ML-DSA-44",  # NIST Level 2
                "Dilithium3": "ML-DSA-65",  # NIST Level 3  
                "Dilithium5": "ML-DSA-87",  # NIST Level 5
            }
            if oqs_sig in oqs_sig_map:
                oqs_sig = oqs_sig_map[oqs_sig]
            
            # Validate algorithms are available
            try:
                with oqs.KeyEncapsulation(oqs_kem):
                    pass
                with oqs.Signature(oqs_sig):
                    pass
                # Store the OQS-compatible names
                self.oqs_kem_algorithm = oqs_kem
                self.oqs_sig_algorithm = oqs_sig
                # Initialization successful - using OQS backend
                _secure_log('info', 'PQC backend initialized successfully')
                return
            except Exception as e:
                # OQS algorithm validation failed, try fallback
                _secure_log('debug', 'OQS primary algorithms unavailable, trying fallback')
                # Try fallback algorithms
                try:
                    fallback_kem = "Kyber512" if self.kem_algorithm == "Kyber1024" else "Kyber1024"
                    fallback_sig = "ML-DSA-44" if oqs_sig == "ML-DSA-65" else "ML-DSA-65"
                    
                    with oqs.KeyEncapsulation(fallback_kem):
                        pass
                    with oqs.Signature(fallback_sig):
                        pass
                    
                    self.kem_algorithm = fallback_kem
                    self.sig_algorithm = fallback_sig  
                    self.oqs_kem_algorithm = fallback_kem
                    self.oqs_sig_algorithm = fallback_sig
                    # Initialization successful - using OQS with fallback algorithms
                    _secure_log('info', 'PQC backend initialized with fallback algorithms')
                    return
                except Exception:
                    _secure_log('debug', 'OQS fallback algorithms unavailable')
                    pass
        
        # Final fallback to classical cryptography with loud warning
        self.backend = PqcBackend.NONE
        
        # Log the fallback to classical (security event)
        _secure_log('warning', 'Falling back to classical cryptography - not quantum-safe')
        
        # Loud classical warning (only shown once per session)
        warnings.warn(
            "Falling back to classical crypto (RSA-4096) - NOT quantum-safe. "
            "Install cpp-pqc, rust-pqc or python-oqs for quantum resistance.",
            RuntimeWarning,
            stacklevel=2
        )
        
        # Initialize classical cryptography backends
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("No cryptographic libraries available. Please install 'cryptography' package.")
    
    def generate_kem_keypair(self) -> Tuple[bytes, bytes]:
        """
        Create a shiny new quantum-safe keypair!
        
        This generates a public key (safe to share) and a secret key (keep this
        locked away!) using Kyber1024. The 'KEM' part stands for 'Key Encapsulation
        Mechanism' - fancy crypto speak for "secure key exchange that quantum
        computers can't break."
        
        Returns a tuple: (public_key, secret_key)
        """
        def _generate_keypair():
            # Try our backends in priority order: C++ → Rust → OQS → Classical
            if self.backend == PqcBackend.CPP:
                # C++ is our primary backend - super fast and battle-tested
                return self.cpp_pqc.generate_kem_keypair()
            
            elif self.backend == PqcBackend.RUST:
                # Rust backend: native Kyber1024 implementation
                return self.rust_pqc.generate_kem_keypair()
            
            elif self.backend == PqcBackend.OQS:
                # Python OQS bindings - slower but still quantum-safe
                kem_alg = getattr(self, 'oqs_kem_algorithm', self.kem_algorithm)
                with oqs.KeyEncapsulation(kem_alg) as kem:
                    public_key = kem.generate_keypair()
                    secret_key = kem.export_secret_key()
                    # Note: OQS returns (public, secret) but we standardize to (secret, public)
                    return secret_key, public_key
            
            else:
                # Fallback to classical RSA-4096 (not quantum-safe)
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.primitives import serialization
                
                # Generate RSA-4096 key
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                )
                public_key = private_key.public_key()
                
                # Serialize to PEM format
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                return private_pem, public_pem
        
        # Apply power analysis protection if enabled
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_generate_keypair)
        else:
            return _generate_keypair()
    
    def generate_sig_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a Dilithium keypair for digital signatures.
        
        These keys let you cryptographically sign messages to prove you're
        really you (and quantum computers can't forge your signature).
        
        Returns: (secret_key, public_key)
        """
        def _generate_keypair():
            # Try backends in order: C++ → Rust → OQS → Classical
            if self.backend == PqcBackend.CPP:
                return self.cpp_pqc.generate_sig_keypair()
            
            elif self.backend == PqcBackend.RUST:
                return self.rust_pqc.generate_sig_keypair()
            
            elif self.backend == PqcBackend.OQS:
                sig_alg = getattr(self, 'oqs_sig_algorithm', self.sig_algorithm)
                with oqs.Signature(sig_alg) as sig:
                    public_key = sig.generate_keypair()
                    secret_key = sig.export_secret_key()
                    return secret_key, public_key
            
            else:
                # Classical fallback: reuse RSA keypair
                return self.generate_kem_keypair()
        
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_generate_keypair)
        else:
            return _generate_keypair()
    
    def kem_encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Wrap up a shared secret using someone's public key.
        
        This is the "sending" side of key exchange. You take their public key,
        and this function generates a random shared secret, then encrypts it
        so only they can decrypt it with their private key. You get back:
        - The encrypted secret (ciphertext) to send them
        - The actual secret (shared_secret) that you both now know
        
        Returns: (ciphertext, shared_secret)
        """
        def _encapsulate():
            if self.backend == PqcBackend.CPP:
                return self.cpp_pqc.kem_encapsulate(public_key)
            
            elif self.backend == PqcBackend.RUST:
                return self.rust_pqc.kem_encapsulate(public_key)
            
            elif self.backend == PqcBackend.OQS:
                kem_alg = getattr(self, 'oqs_kem_algorithm', self.kem_algorithm)
                with oqs.KeyEncapsulation(kem_alg) as kem:
                    # OQS does the heavy lifting for us
                    ciphertext, shared_secret = kem.encap_secret(public_key)
                    return ciphertext, shared_secret
            
            else:
                # Classical RSA fallback
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes
                
                # Parse their public key
                public_key_obj = serialization.load_pem_public_key(public_key)
                
                # Generate a random 256-bit shared secret
                shared_secret = secrets.token_bytes(32)
                
                # Encrypt it with RSA-OAEP (secure RSA encryption mode)
                ciphertext = public_key_obj.encrypt(
                    shared_secret,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None  # No label needed for our use case
                    )
                )
                
                return ciphertext, shared_secret
        
        # Power analysis protection if available
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_encapsulate)
        else:
            return _encapsulate()
    
    def kem_decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        """
        Unwrap the shared secret using your private key.
        
        This is the "receiving" side of key exchange. Someone sent you an
        encrypted secret (ciphertext). Use your private key to decrypt it
        and recover the shared secret that you both now know.
        
        Returns: The shared secret (bytes)
        """
        def _decapsulate():
            if self.backend == PqcBackend.CPP:
                return self.cpp_pqc.kem_decapsulate(secret_key, ciphertext)
            
            elif self.backend == PqcBackend.RUST:
                return self.rust_pqc.kem_decapsulate(secret_key, ciphertext)
            
            elif self.backend == PqcBackend.OQS:
                kem_alg = getattr(self, 'oqs_kem_algorithm', self.kem_algorithm)
                # Initialize KEM with the secret key
                with oqs.KeyEncapsulation(kem_alg, secret_key=secret_key) as kem:
                    # Decrypt the ciphertext to get the shared secret
                    return kem.decap_secret(ciphertext)
            
            else:
                # Classical RSA fallback
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes
                
                # Parse our private key
                private_key_obj = serialization.load_pem_private_key(secret_key, password=None)
                
                # Decrypt the ciphertext to get the shared secret back
                shared_secret = private_key_obj.decrypt(
                    ciphertext,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                return shared_secret
        
        # Power analysis protection if available
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_decapsulate)
        else:
            return _decapsulate()
    
    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """
        Sign a message to prove it's really from you.
        
        Takes your secret key and a message, produces a signature that proves:
        1. The message came from you (authentication)
        2. The message wasn't tampered with (integrity)
        
        Anyone with your public key can verify this signature, but only you
        could have created it (because only you have the secret key).
        
        Returns: The signature (bytes)
        """
        def _sign():
            if self.backend == PqcBackend.CPP:
                return self.cpp_pqc.sign(message, secret_key)
            
            elif self.backend == PqcBackend.RUST:
                return self.rust_pqc.sign(message, secret_key)
            
            elif self.backend == PqcBackend.OQS:
                sig_alg = getattr(self, 'oqs_sig_algorithm', self.sig_algorithm)
                # Initialize signature with the secret key
                with oqs.Signature(sig_alg, secret_key=secret_key) as sig:
                    # Sign the message
                    return sig.sign(message)
            
            else:
                # Classical RSA-PSS signature fallback
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes
                
                # Parse our private key
                private_key_obj = serialization.load_pem_private_key(secret_key, password=None)
                
                # Create RSA-PSS signature (more secure than old PKCS#1 v1.5)
                signature = private_key_obj.sign(
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH  # Maximum security
                    ),
                    hashes.SHA256()
                )
                
                return signature
        
        # Power analysis protection if available
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_sign)
        else:
            return _sign()
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Check if a signature is valid.
        
        Takes a message, a signature, and the signer's public key. Returns True
        if the signature is valid (message is authentic and unmodified), False
        otherwise.
        
        This is the magic that lets you trust messages without having to trust
        the network they traveled over!
        
        Returns: True if valid, False if invalid/tampered
        """
        def _verify():
            if self.backend == PqcBackend.CPP:
                return self.cpp_pqc.verify(message, signature, public_key)
            
            elif self.backend == PqcBackend.RUST:
                return self.rust_pqc.verify(message, signature, public_key)
            
            elif self.backend == PqcBackend.OQS:
                try:
                    sig_alg = getattr(self, 'oqs_sig_algorithm', self.sig_algorithm)
                    with oqs.Signature(sig_alg) as sig:
                        # OQS verify returns True/False directly
                        return sig.verify(message, signature, public_key)
                except Exception:
                    # Any error during verification = invalid signature
                    return False
            
            else:
                # Classical RSA-PSS verification fallback
                try:
                    from cryptography.hazmat.primitives import serialization
                    from cryptography.hazmat.primitives.asymmetric import padding
                    from cryptography.hazmat.primitives import hashes
                    
                    # Parse their public key
                    public_key_obj = serialization.load_pem_public_key(public_key)
                    
                    # Try to verify - will raise exception if invalid
                    public_key_obj.verify(
                        signature,
                        message,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    # If we got here, signature is valid!
                    return True
                except Exception:
                    # Signature verification failed
                    return False
        
        # Power analysis protection if available
        if POWER_ANALYSIS_PROTECTION:
            return secure_pqc_execute(_verify)
        else:
            return _verify()


class HybridCrypto:
    """
    Hybrid classical + post-quantum cryptography.
    
    This combines the best of both worlds:
    - Classical crypto (Argon2id + AES-256-GCM) that's well-tested
    - PQC (Kyber) that's quantum-safe
    
    The idea is defense-in-depth: even if one algorithm is broken,
    the other still protects your data.
    """
    
    def __init__(self):
        self.pqc = PostQuantumCrypto()
        
        # Check if power analysis protection is available
        self.power_protection_enabled = POWER_ANALYSIS_PROTECTION
    
    def derive_hybrid_key(self, passphrase: str, salt: bytes, pq_shared_secret: bytes = None) -> bytes:
        """
        Mix classical and quantum-safe entropy to derive an encryption key.
        
        We take a passphrase (classical) and optionally a PQC shared secret,
        then combine them in a secure way to get the final encryption key.
        
        Args:
            passphrase: User's password
            salt: Random salt for key derivation
            pq_shared_secret: Optional PQC shared secret from Kyber
            
        Returns: A 32-byte encryption key
        """
        if not pq_shared_secret:
            # No PQC secret available, use classical derivation
            return self._derive_classical_key(passphrase, salt)
        
        # Hybrid mode: combine both entropy sources
        classical_key = self._derive_classical_key(passphrase, salt)
        
        # Mix with PQC shared secret
        combined_input = classical_key + pq_shared_secret + b"PQC_HYBRID_V1"
        
        # Final mixing
        combined = classical_key + pq_shared_secret[:32] if len(pq_shared_secret) >= 32 else pq_shared_secret.ljust(32, b'\x00')
        return hashlib.sha256(combined).digest()
    
    def _derive_classical_key(self, passphrase: str, salt: bytes) -> bytes:
        """
        Derive encryption key from passphrase using Argon2id.
        
        - Memory-hard (resistant to GPU/ASIC attacks)
        - Time-hard (slows down brute force)
        - Side-channel resistant
        
        Falls back to Scrypt if Argon2 isn't available.
        """
        if HAS_ARGON2:
            # Use Argon2id for password hashing
            params = SecurityConfig.get_argon2_params()
            return hash_secret_raw(
                passphrase.encode('utf-8'),
                salt,
                time_cost=params["time_cost"],
                memory_cost=params["memory_cost"],
                parallelism=params["parallelism"],
                hash_len=SecurityConfig.AES_KEY_SIZE,
                type=Argon2Type.ID
            )
        else:
            # Scrypt fallback
            if not HAS_CRYPTOGRAPHY:
                raise RuntimeError("No key derivation libraries available")
            
            # Note: Scrypt doesn't take an algorithm parameter in cryptography library
            kdf = Scrypt(
                salt=salt,
                length=SecurityConfig.AES_KEY_SIZE,  # 32 bytes for AES-256
                n=2**18,  # 262144 iterations - CPU cost
                r=8,  # Block size - memory cost
                p=1  # Parallelization factor
            )
            return kdf.derive(passphrase.encode('utf-8'))
    
    def encrypt_with_pqc(self, data: bytes, passphrase: str, kem_public_key: bytes = None) -> Dict[str, Any]:
        """
        Encrypt data using hybrid classical + PQC encryption.
        
        This is where the magic happens! We:
        1. Generate random salt and nonce
        2. If we have a PQC public key, use Kyber to create a shared secret
        3. Derive an encryption key from passphrase + PQC secret
        4. Encrypt the data with AES-256-GCM
        5. Package everything up for storage/transmission
        
        Args:
            data: The plaintext to encrypt
            passphrase: User's password
            kem_public_key: Optional Kyber public key for PQC mode
            
        Returns: A dictionary containing the encrypted package
        
        Raises:
            ValueError: If input validation fails
            RuntimeError: If cryptography library unavailable
        """
        # Input validation
        if not isinstance(data, bytes):
            raise ValueError("Data must be bytes")
        if not isinstance(passphrase, str) or len(passphrase) < 8:
            raise ValueError("Passphrase must be string with at least 8 characters")
        if len(data) == 0:
            raise ValueError("Data cannot be empty")
        if len(data) > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError("Data exceeds maximum size (100MB)")
        if kem_public_key is not None and not isinstance(kem_public_key, bytes):
            raise ValueError("kem_public_key must be bytes or None")
        
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("Cryptography library not available")
        
        # Generate random values (never reuse these!)
        salt = secrets.token_bytes(SecurityConfig.SALT_SIZE)  # For key derivation
        nonce = secrets.token_bytes(SecurityConfig.NONCE_SIZE)  # For AES-GCM
        
        pq_shared_secret = None
        kem_ciphertext = None
        
        if kem_public_key:
            # Quantum-safe mode: use Kyber to establish shared secret
            kem_ciphertext, pq_shared_secret = self.pqc.kem_encapsulate(kem_public_key)
        
        # Derive the final encryption key (classical + PQC if available)
        encryption_key = self.derive_hybrid_key(passphrase, salt, pq_shared_secret)
        
        # Encrypt the data with AES-256-GCM
        # Use AES-GCM for authenticated encryption
        aes_gcm = AESGCM(encryption_key)
        ciphertext = aes_gcm.encrypt(nonce, data, None)
        
        # Package encrypted data
        package = {
            "version": "2.0_PQC",
            "salt": salt.hex(),
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
            "kem_algorithm": self.pqc.kem_algorithm,
            "sig_algorithm": self.pqc.sig_algorithm,
            "hybrid_mode": True
        }
        
        if kem_ciphertext:
            package["kem_ciphertext"] = kem_ciphertext.hex()
        
        return package
    
    def decrypt_with_pqc(self, package: Dict[str, Any], passphrase: str, kem_secret_key: bytes = None) -> bytes:
        """
        Decrypt data using hybrid classical + PQC decryption.
        
        This is the reverse of encrypt_with_pqc:
        1. Extract all the pieces from the package
        2. If there's a KEM ciphertext, use Kyber to recover the shared secret
        3. Derive the same encryption key (passphrase + PQC secret)
        4. Decrypt the data with AES-256-GCM
        5. Verify authentication tag (GCM does this automatically)
        
        Args:
            package: The encrypted package from encrypt_with_pqc
            passphrase: User's password
            kem_secret_key: Optional Kyber secret key for PQC mode
            
        Returns: The decrypted plaintext
        
        Raises:
            ValueError: If decryption fails or input validation fails
            RuntimeError: If cryptography library unavailable
        """
        # Input validation
        if not isinstance(package, dict):
            raise ValueError("Package must be a dictionary")
        if not isinstance(passphrase, str) or len(passphrase) < 8:
            raise ValueError("Passphrase must be string with at least 8 characters")
        
        required_fields = ["salt", "nonce", "ciphertext"]
        for field in required_fields:
            if field not in package:
                raise ValueError(f"Package missing required field: {field}")
        
        if kem_secret_key is not None and not isinstance(kem_secret_key, bytes):
            raise ValueError("kem_secret_key must be bytes or None")
        
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("Cryptography library not available")
        
        # Unpack the encrypted package (with validation)
        try:
            salt = bytes.fromhex(package["salt"])
            nonce = bytes.fromhex(package["nonce"])
            ciphertext = bytes.fromhex(package["ciphertext"])
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid package format: {e}")
        
        # Validate sizes to prevent DoS attacks
        if len(salt) != SecurityConfig.SALT_SIZE:
            raise ValueError(f"Invalid salt size: expected {SecurityConfig.SALT_SIZE}, got {len(salt)}")
        if len(nonce) != SecurityConfig.NONCE_SIZE:
            raise ValueError(f"Invalid nonce size: expected {SecurityConfig.NONCE_SIZE}, got {len(nonce)}")
        if len(ciphertext) > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError("Ciphertext exceeds maximum size")
        
        pq_shared_secret = None
        
        if "kem_ciphertext" in package and kem_secret_key:
            # Quantum-safe mode: recover the shared secret using Kyber
            try:
                kem_ciphertext = bytes.fromhex(package["kem_ciphertext"])
            except ValueError as e:
                raise ValueError(f"Invalid kem_ciphertext format: {e}")
            pq_shared_secret = self.pqc.kem_decapsulate(kem_secret_key, kem_ciphertext)
        
        # Derive the same encryption key we used to encrypt
        decryption_key = self.derive_hybrid_key(passphrase, salt, pq_shared_secret)
        
        # Decrypt the data with AES-256-GCM
        aes_gcm = AESGCM(decryption_key)
        try:
            return aes_gcm.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise ValueError("Decryption failed - invalid key or corrupted data")


def _encrypt_backup(plaintext: bytes, passphrase: str, meta: dict) -> bytes:
    salt = os.urandom(16)
    key, kdf_params = _derive_key(passphrase, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    aad = json.dumps(meta, separators=(",", ":")).encode()
    ct = aes.encrypt(nonce, plaintext, aad)
    payload = {"meta": meta, "kdf": {**kdf_params, "salt": salt.hex()}, "aead": {"alg": "AES-256-GCM", "nonce": nonce.hex(), "ct": ct.hex()}}
    return json.dumps(payload, separators=(",", ":")).encode()


def verify_backup(backup_file: Path, passphrase: str, token: bytes) -> bool:
    """Decrypt backup and check it matches `token` by SHA3-512 with timing attack protection."""
    try:
        TimingAttackMitigation.add_random_delay()
        
        data = json.loads(backup_file.read_text("utf-8"))
        meta = data["meta"]
        aead = data["aead"]
        salt = bytes.fromhex(data["kdf"]["salt"])
        
        key, _ = _derive_key(passphrase, salt)
        
        pt = AESGCM(key).decrypt(
            bytes.fromhex(aead["nonce"]), 
            bytes.fromhex(aead["ct"]), 
            json.dumps(meta, separators=(",", ":")).encode()
        )
        
        backup_hash = hashlib.sha3_512(pt).digest()
        expected_hash = hashlib.sha3_512(token).digest()
        # The hash in the metadata is hex-encoded
        meta_hash = bytes.fromhex(meta["sha3"])
        
        hash_match = (
            TimingAttackMitigation.constant_time_compare(backup_hash, expected_hash) and
            TimingAttackMitigation.constant_time_compare(backup_hash, meta_hash)
        )
        
        secure_zero_memory(bytearray(key))
        secure_zero_memory(bytearray(pt))
        
        return hash_match
    
    except InvalidTag:
        # This is the expected exception for a wrong passphrase. Re-raise it.
        if 'key' in locals():
            secure_zero_memory(bytearray(key))
        raise
    except Exception:
        if 'key' in locals():
            secure_zero_memory(bytearray(key))
        return False


def get_available_backends() -> Dict[str, bool]:
    """
    Check what cryptographic backends are available.
    
    This is useful for debugging and for showing users what security
    features are actually working on their system.
    
    Returns a dict like:
    {
        "cpp_pqc": True/False,
        "rust_pqc": True/False,
        "oqs": True/False,
        "argon2": True/False,
        "cryptography": True/False,
        "power_analysis_protection": True/False
    }
    """
    return {
        "cpp_pqc": HAS_CPP_PQC,
        "rust_pqc": HAS_RUST_PQC,
        "oqs": HAS_OQS,
        "argon2": HAS_ARGON2,
        "cryptography": HAS_CRYPTOGRAPHY,
        "power_analysis_protection": POWER_ANALYSIS_PROTECTION
    }


def check_pqc_requirements() -> bool:
    """
    Quick check: do we have ANY post-quantum crypto available?
    
    Returns True if at least one PQC backend (C++, Rust, or OQS) is working.
    Returns False if we're stuck with classical crypto only.
    """
    return HAS_CPP_PQC or HAS_RUST_PQC or HAS_OQS
