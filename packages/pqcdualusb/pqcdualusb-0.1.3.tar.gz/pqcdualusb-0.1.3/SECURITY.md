# Security Policy

We take the security of this project seriously. If you discover a security vulnerability, please follow these guidelines to report it responsibly.

## Supported Versions

The following table shows which versions of the library are currently supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please send an email to the maintainer at **`Johnsonajibi@gmail.com`**.

Please include the following information in your report:

-   A descriptive title, e.g., `[SECURITY] Remote Code Execution in...`
-   The version of the library you are using.
-   A detailed description of the vulnerability.
-   Step-by-step instructions on how to reproduce the issue.
-   Any proof-of-concept code or scripts.
-   The potential impact of the vulnerability.

### Response Timeline

You can expect the following response timeline:

-   **Initial Acknowledgment**: Within 48 hours.
-   **Initial Assessment**: Within 1 week.
-   **Progress Updates**: We will strive to provide updates every 7-14 days until a fix is released.
-   **Public Disclosure**: We will coordinate with you to disclose the vulnerability publicly after a fix has been released.

## Security Measures in This Library

This library is designed with a "secure-by-default" philosophy and incorporates several layers of defense.

### Cryptographic Security
-   **Hybrid Encryption**: Combines classical AES-256-GCM with post-quantum Kyber1024 to protect against both current and future threats.
-   **Post-Quantum Signatures**: Uses NIST-standardized Dilithium3 for verifying the authenticity of audit logs and other critical data.
-   **Strong Key Derivation**: Employs Argon2id, a memory-hard function, to stretch user passphrases and resist brute-force attacks.
-   **Timing Attack Mitigation**: Uses constant-time comparison functions for cryptographic secrets.

### System and Memory Security
-   **Secure Memory Wiping**: Automatically zeroes out memory that held sensitive data (keys, plaintexts) to prevent data leakage from memory dumps or cold boot attacks.
-   **Atomic File Operations**: Uses atomic writes to prevent data corruption or partial writes in case of an unexpected shutdown.
-   **Input Validation**: All inputs, especially file paths and passphrases, are strictly validated to prevent vulnerabilities like path traversal.
-   **Device Validation**: The library includes functions to ensure that backups are being written to distinct, removable physical devices, preventing accidental overwrites.

### Audit and Tamper-Evidence
-   **Secure Logging**: All critical security events are logged to a local, append-only file.
-   **HMAC Chaining**: Each log entry is chained to the previous one with an HMAC, making it computationally infeasible to tamper with the log without detection.

## Security Testing

-   **Unit and Integration Tests**: The test suite includes specific tests for cryptographic correctness, exception handling on invalid inputs, and proper memory cleanup.
-   **Static Analysis**: The codebase is regularly scanned with tools like `flake8` and `mypy` to catch potential issues early.
-   **Code Review**: All contributions, especially those touching security-sensitive code, undergo a manual security review.

Thank you for helping to keep the PQC Dual USB Library secure.
