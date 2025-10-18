"""
Security Configuration and Memory Management
===========================================

Core security utilities and configuration for the pqcdualusb library.

Components:
- SecureMemory: Secure memory allocation with automatic cleanup
- TimingAttackMitigation: Countermeasures against timing-based attacks
- SecurityConfig: Centralized security configuration and constants

Provides foundational security functionality including secure memory handling,
timing attack prevention, and security parameter configuration.
"""

import os
import sys
import time
import secrets
import platform
import ctypes
import mmap
from typing import Union, List, Dict, Any
from pathlib import Path


class SecureMemory:
    """
    Secure memory allocation with automatic cleanup.
    
    Provides secure memory allocation for sensitive data such as passwords
    and cryptographic keys. Automatically overwrites memory with zeros on
    cleanup to prevent data recovery. Attempts to prevent memory from being
    swapped to disk where possible.
    
    Used for storing sensitive data with guaranteed secure cleanup.
    """
    
    def __init__(self, size: int):
        self.size = size
        self.data = None
        self.locked = False
        
        # Allocate secure buffer
        self.data = bytearray(size)
        
        # Try to lock memory to prevent swapping
        if platform.system() == "Windows":
            self._lock_memory_windows()
        else:
            self._lock_memory_posix()
    
    def __enter__(self):
        return self.data
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
    
    def _lock_memory_windows(self):
        """Lock memory on Windows using VirtualLock."""
        try:
            import ctypes
            from ctypes import wintypes
            
            kernel32 = ctypes.windll.kernel32
            addr = ctypes.addressof((ctypes.c_char * len(self.data)).from_buffer(self.data))
            
            if kernel32.VirtualLock(ctypes.c_void_p(addr), ctypes.c_size_t(len(self.data))):
                self.locked = True
        except Exception:
            # Memory locking failed, continue without it
            pass
    
    def _lock_memory_posix(self):
        """Lock memory on POSIX systems using mlock."""
        try:
            # Get libc handle
            if platform.system() == "Darwin":  # macOS
                libc = ctypes.CDLL("libc.dylib")
            else:  # Linux and other POSIX
                libc = ctypes.CDLL("libc.so.6")
            
            # Get memory address
            addr = ctypes.addressof((ctypes.c_char * len(self.data)).from_buffer(self.data))
            
            # Call mlock system call
            if libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(self.data))) == 0:
                self.locked = True
        except Exception:
            # Memory locking failed, continue without it
            pass
    
    def _cleanup(self):
        """Securely zero and unlock memory."""
        if self.data:
            # Zero the memory
            secure_zero_memory(self.data)
            
            # Unlock memory if it was locked
            if self.locked:
                try:
                    if platform.system() == "Windows":
                        kernel32 = ctypes.windll.kernel32
                        addr = ctypes.addressof((ctypes.c_char * len(self.data)).from_buffer(self.data))
                        kernel32.VirtualUnlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(self.data)))
                    else:
                        # Get libc handle for munlock
                        if platform.system() == "Darwin":  # macOS
                            libc = ctypes.CDLL("libc.dylib")
                        else:  # Linux and other POSIX
                            libc = ctypes.CDLL("libc.so.6")
                        
                        addr = ctypes.addressof((ctypes.c_char * len(self.data)).from_buffer(self.data))
                        libc.munlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(self.data)))
                except Exception:
                    pass
            
            self.data = None


class TimingAttackMitigation:
    """
    Advanced timing attack mitigation for cryptographic operations.
    
    Implements multiple defense techniques:
    - Constant-time comparisons
    - Random delays with exponential distribution
    - Operation padding to fixed time windows
    - Statistical timing noise
    """
    
    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks.
        
        Uses bitwise operations to ensure comparison time is independent
        of where differences occur in the byte sequences.
        
        Args:
            a: First byte sequence
            b: Second byte sequence
        
        Returns:
            True if sequences are equal, False otherwise
        """
        # Length check must also be constant-time
        length_match = len(a) == len(b)
        
        # Pad to same length for constant-time comparison
        if not length_match:
            # Pad shorter sequence to avoid early termination
            max_len = max(len(a), len(b))
            a = a.ljust(max_len, b'\x00')
            b = b.ljust(max_len, b'\x00')
        
        # XOR all bytes - result is 0 only if all bytes match
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        # Return True only if both length matched AND all bytes matched
        return length_match and (result == 0)
    
    @staticmethod
    def constant_time_select(condition: bool, true_value: int, false_value: int) -> int:
        """
        Constant-time conditional selection.
        
        Selects between two values based on a condition without branching,
        preventing timing attacks based on conditional execution paths.
        
        Args:
            condition: Boolean condition
            true_value: Value to return if condition is True
            false_value: Value to return if condition is False
        
        Returns:
            Selected value
        """
        # Convert bool to int: True=1, False=0
        selector = int(condition)
        
        # Bitwise selection without branching
        # If selector=1: returns true_value
        # If selector=0: returns false_value
        return (selector * true_value) | ((1 - selector) * false_value)
    
    @staticmethod
    def add_random_delay(min_ms: int = None, max_ms: int = None):
        """
        Add random delay with exponential distribution.
        
        Uses exponential distribution rather than uniform to better
        obfuscate timing patterns in statistical analysis.
        
        Args:
            min_ms: Minimum delay in milliseconds (default: 1)
            max_ms: Maximum delay in milliseconds (default: 10)
        """
        min_delay = (min_ms or 1) / 1000.0
        max_delay = (max_ms or 10) / 1000.0
        
        # Exponential distribution for timing variation
        import math
        lambda_param = 2.0
        
        # Generate exponential random value
        uniform = secrets.randbelow(1000000) / 1000000.0
        exp_value = -math.log(1 - uniform) / lambda_param
        
        # Scale to desired range
        delay = min_delay + (exp_value * (max_delay - min_delay))
        delay = min(delay, max_delay)  # Cap at maximum
        
        time.sleep(delay)
    
    @staticmethod
    def pad_to_fixed_time(target_ms: float, start_time: float = None):
        """
        Pad operation to fixed time window.
        
        Ensures an operation takes at least a fixed amount of time,
        preventing timing attacks based on operation duration.
        
        Args:
            target_ms: Target duration in milliseconds
            start_time: Start time (if None, uses current time)
        """
        if start_time is None:
            start_time = time.perf_counter()
        
        elapsed = (time.perf_counter() - start_time) * 1000
        remaining = target_ms - elapsed
        
        if remaining > 0:
            # Add remaining time plus small random jitter
            jitter = secrets.randbelow(1000) / 1000.0  # 0-1ms
            time.sleep((remaining + jitter) / 1000.0)
    
    @staticmethod
    def add_statistical_noise(operation_count: int = None):
        """
        Add statistical timing noise to obfuscate patterns.
        
        Performs a variable number of dummy operations to add
        noise to timing measurements, making statistical analysis harder.
        
        Args:
            operation_count: Number of dummy operations (random if None)
        """
        if operation_count is None:
            # Random count with Poisson-like distribution
            operation_count = secrets.randbelow(100) + 20
        
        # Dummy operations with varying complexity
        dummy = secrets.token_bytes(16)
        for i in range(operation_count):
            # Variable complexity operations
            if i % 3 == 0:
                # Simple XOR
                dummy = bytes(a ^ b for a, b in zip(dummy, secrets.token_bytes(16)))
            elif i % 3 == 1:
                # Bit rotation
                value = int.from_bytes(dummy, 'big')
                value = (value << 3) | (value >> 125)
                dummy = value.to_bytes(16, 'big')
            else:
                # Modular arithmetic
                value = int.from_bytes(dummy, 'big')
                value = (value * 31337) % (2**128 - 1)
                dummy = value.to_bytes(16, 'big')
    
    @classmethod
    def protect_comparison(cls, a: bytes, b: bytes) -> bool:
        """
        Protected comparison with timing attack mitigation.
        
        Combines constant-time comparison with random delays
        for defense-in-depth against timing attacks.
        
        Args:
            a: First byte sequence
            b: Second byte sequence
        
        Returns:
            True if sequences are equal
        """
        # Add pre-comparison noise
        cls.add_statistical_noise(secrets.randbelow(50) + 10)
        
        # Constant-time comparison
        result = cls.constant_time_compare(a, b)
        
        # Add post-comparison noise
        cls.add_random_delay(1, 5)
        
        return result


class SecurityConfig:
    """Security configuration and validation."""
    
    # Post-quantum algorithms
    PQC_KEM_ALGORITHM = "Kyber1024"
    PQC_SIG_ALGORITHM = "Dilithium3"
    
    # Classical cryptography  
    AES_KEY_SIZE = 32  # 256-bit
    SALT_SIZE = 32
    NONCE_SIZE = 12
    HMAC_KEY_SIZE = 32
    
    # Argon2id parameters
    ARGON2_TIME_COST = 4
    ARGON2_MEMORY_COST = 65536  # 64 MB
    ARGON2_PARALLELISM = 2
    
    # Security levels
    PQC_HYBRID_MODE = True               # Use hybrid classical+PQC
    ENFORCE_DEVICE_BINDING = True        # Check device identifiers
    REQUIRE_REMOVABLE_DRIVES = True      # Only use removable USB drives
    ENABLE_AUDIT_LOGGING = True          # Tamper-evident audit logs
    MINIMUM_TOKEN_SIZE = 32              # Minimum token size in bytes
    MAXIMUM_TOKEN_SIZE = 1024            # Maximum token size in bytes
    MINIMUM_PASSPHRASE_LENGTH = 12       # Minimum passphrase length
    
    # Power analysis countermeasures
    ENABLE_TIMING_RANDOMIZATION = True   # Add random delays
    ENABLE_POWER_BALANCING = True        # Power consumption balancing

    # Audit log settings
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_LOG_FILES = 5
    
    @classmethod
    def get_argon2_params(cls) -> Dict[str, int]:
        """Get Argon2id parameters for key derivation."""
        return {
            "time_cost": cls.ARGON2_TIME_COST,
            "memory_cost": cls.ARGON2_MEMORY_COST,
            "parallelism": cls.ARGON2_PARALLELISM
        }
    
    @classmethod
    def validate_security_level(cls) -> List[str]:
        """
        Validate current security configuration and return warnings.
        
        Returns:
            List of security warnings or recommendations
        """
        warnings = []
        
        # Check key sizes
        if cls.AES_KEY_SIZE < 32:
            warnings.append("AES key size below 256 bits - consider increasing")
        
        if cls.SALT_SIZE < 16:
            warnings.append("Salt size below 128 bits - consider increasing")
        
        # Check Argon2 parameters
        if cls.ARGON2_MEMORY_COST < 32768:  # 32 MB
            warnings.append("Argon2 memory cost may be too low for high security")
        
        if cls.ARGON2_TIME_COST < 3:
            warnings.append("Argon2 time cost may be too low for high security")
        
        # Check minimum sizes
        if cls.MINIMUM_TOKEN_SIZE < 32:
            warnings.append("Minimum token size below 256 bits")
        
        if cls.MINIMUM_PASSPHRASE_LENGTH < 12:
            warnings.append("Minimum passphrase length may be too short")
        
        # Check security features
        if not cls.PQC_HYBRID_MODE:
            warnings.append("PQC hybrid mode disabled - quantum vulnerability possible")
        
        if not cls.ENFORCE_DEVICE_BINDING:
            warnings.append("Device binding disabled - cloning attacks possible")
        
        if not cls.REQUIRE_REMOVABLE_DRIVES:
            warnings.append("Non-removable drives allowed - air-gap security reduced")
        
        return warnings


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = True, must_be_dir: bool = False) -> Path:
        """
        Validate and normalize a file system path.
        
        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            must_be_dir: Whether the path must be a directory
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If validation fails
        """
        if not path:
            raise ValueError("Path cannot be empty")
        
        path_obj = Path(path).resolve()
        
        if must_exist and not path_obj.exists():
            raise ValueError(f"Path does not exist: {path_obj}")
        
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path_obj}")
        
        return path_obj
    
    @staticmethod
    def validate_passphrase(passphrase: str, min_length: int = None) -> str:
        """
        Validate passphrase strength.
        
        Args:
            passphrase: Passphrase to validate
            min_length: Minimum required length
            
        Returns:
            Validated passphrase
            
        Raises:
            ValueError: If validation fails
        """
        if not passphrase:
            raise ValueError("Passphrase cannot be empty")
        
        min_len = min_length or SecurityConfig.MINIMUM_PASSPHRASE_LENGTH
        
        if len(passphrase) < min_len:
            raise ValueError(f"Passphrase must be at least {min_len} characters")
        
        # Check for common weak patterns
        if passphrase.lower() in ['password', '123456', 'qwerty', 'admin']:
            raise ValueError("Passphrase is too common - use a stronger passphrase")
        
        return passphrase
    
    @staticmethod
    def validate_token_size(size: int, min_size: int = None, max_size: int = None) -> int:
        """
        Validate token size.
        
        Args:
            size: Token size in bytes
            min_size: Minimum allowed size
            max_size: Maximum allowed size
            
        Returns:
            Validated size
            
        Raises:
            ValueError: If validation fails
        """
        min_s = min_size or SecurityConfig.MINIMUM_TOKEN_SIZE
        max_s = max_size or SecurityConfig.MAXIMUM_TOKEN_SIZE
        
        if size < min_s:
            raise ValueError(f"Token size must be at least {min_s} bytes")
        
        if size > max_s:
            raise ValueError(f"Token size cannot exceed {max_s} bytes")
        
        return size


def secure_zero_memory(data: Union[bytearray, bytes]) -> None:
    """
    Securely zero memory contents.
    
    This function attempts to prevent compiler optimizations from removing
    the memory clearing operation.
    
    Args:
        data: Memory buffer to zero (bytearray or bytes)
    """
    if isinstance(data, bytearray):
        # Zero the bytearray in place
        for i in range(len(data)):
            data[i] = 0
        
        # Additional security: try to prevent optimization
        try:
            # Force memory barrier on supported platforms
            if platform.system() == "Windows":
                ctypes.windll.kernel32.MemoryBarrier()
            else:
                # On POSIX, try to use memory barrier if available
                try:
                    import ctypes.util
                    libc = ctypes.CDLL(ctypes.util.find_library("c"))
                    if hasattr(libc, '__sync_synchronize'):
                        libc.__sync_synchronize()
                except:
                    pass
        except:
            pass
    
    elif isinstance(data, bytes):
        # Cannot modify bytes object, warn user
        import warnings
        warnings.warn("Cannot securely zero immutable bytes object", RuntimeWarning)


def get_security_info() -> Dict[str, Any]:
    """Get comprehensive security configuration information."""
    return {
        "algorithms": {
            "pqc_kem": SecurityConfig.PQC_KEM_ALGORITHM,
            "pqc_sig": SecurityConfig.PQC_SIG_ALGORITHM,
            "aes_key_bits": SecurityConfig.AES_KEY_SIZE * 8,
            "salt_bits": SecurityConfig.SALT_SIZE * 8,
            "hmac_key_bits": SecurityConfig.HMAC_KEY_SIZE * 8
        },
        "argon2": SecurityConfig.get_argon2_params(),
        "security_features": {
            "pqc_hybrid_mode": SecurityConfig.PQC_HYBRID_MODE,
            "device_binding": SecurityConfig.ENFORCE_DEVICE_BINDING,
            "removable_only": SecurityConfig.REQUIRE_REMOVABLE_DRIVES,
            "audit_logging": SecurityConfig.ENABLE_AUDIT_LOGGING,
            "timing_randomization": SecurityConfig.ENABLE_TIMING_RANDOMIZATION,
            "power_balancing": SecurityConfig.ENABLE_POWER_BALANCING
        },
        "limits": {
            "min_token_size": SecurityConfig.MINIMUM_TOKEN_SIZE,
            "max_token_size": SecurityConfig.MAXIMUM_TOKEN_SIZE,
            "min_passphrase_len": SecurityConfig.MINIMUM_PASSPHRASE_LENGTH
        },
        "warnings": SecurityConfig.validate_security_level()
    }
