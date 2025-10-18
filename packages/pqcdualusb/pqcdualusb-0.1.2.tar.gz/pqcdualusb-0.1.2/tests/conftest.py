"""
Test configuration for pytest.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_usb_drives(temp_dir: Path) -> tuple[Path, Path]:
    """Create mock USB drive directories for testing."""
    primary = temp_dir / "primary_usb"
    backup = temp_dir / "backup_usb"
    
    primary.mkdir()
    backup.mkdir()
    
    return primary, backup


@pytest.fixture
def test_secret() -> bytes:
    """Generate a test secret."""
    return b"test_secret_data_12345678901234567890123456789012"


@pytest.fixture
def test_passphrase() -> str:
    """Provide a test passphrase."""
    return "test_passphrase_with_sufficient_complexity_123!"
