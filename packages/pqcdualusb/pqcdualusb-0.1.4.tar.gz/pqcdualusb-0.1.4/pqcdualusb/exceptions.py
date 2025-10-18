"""
exceptions.py
==============================================
Custom exceptions for the application.
"""

class CliUsageError(Exception):
    """Custom exception for CLI usage errors."""
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
