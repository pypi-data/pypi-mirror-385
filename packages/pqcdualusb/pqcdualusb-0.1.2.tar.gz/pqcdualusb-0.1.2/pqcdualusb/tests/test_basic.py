"""
Basic Library Test
==================

Basic test to verify the library structure is working.
"""

import unittest
import sys
from pathlib import Path

# Add the parent directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from pqcdualusb import PostQuantumCrypto, UsbDriveDetector, SecurityConfig
    from pqcdualusb.crypto import get_available_backends, check_pqc_requirements
    from pqcdualusb.usb import get_drive_selection_info
    from pqcdualusb.utils import ProgressReporter, InputValidator
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestLibraryStructure(unittest.TestCase):
    """Test basic library structure and imports."""
    
    def test_imports_work(self):
        """Test that all main imports work."""
        self.assertTrue(IMPORTS_AVAILABLE, f"Import failed: {IMPORT_ERROR if not IMPORTS_AVAILABLE else 'N/A'}")
    
    @unittest.skipUnless(IMPORTS_AVAILABLE, "Imports not available")
    def test_crypto_backend_info(self):
        """Test that we can get crypto backend information."""
        backends = get_available_backends()
        self.assertIsInstance(backends, dict)
        self.assertIn("rust_pqc", backends)
        self.assertIn("oqs", backends)
        self.assertIn("power_analysis_protection", backends)
    
    @unittest.skipUnless(IMPORTS_AVAILABLE, "Imports not available")
    def test_usb_detection(self):
        """Test USB drive detection functionality."""
        drives = UsbDriveDetector.get_removable_drives()
        self.assertIsInstance(drives, list)
        
        # Test drive info function
        drive_info = get_drive_selection_info()
        self.assertIsInstance(drive_info, dict)
        self.assertIn("total_drives", drive_info)
        self.assertIn("platform", drive_info)
    
    @unittest.skipUnless(IMPORTS_AVAILABLE, "Imports not available")
    def test_progress_reporter(self):
        """Test progress reporting functionality."""
        progress = ProgressReporter(1000, "Test Operation")
        progress.update(100)
        progress.update(200)
        progress.finish()
        
        self.assertEqual(progress.processed_bytes, 300)
        self.assertTrue(progress._finished)
    
    @unittest.skipUnless(IMPORTS_AVAILABLE, "Imports not available")
    def test_input_validation(self):
        """Test input validation functions."""
        # Test token size validation
        valid_size = InputValidator.validate_token_size(64)
        self.assertEqual(valid_size, 64)
        
        with self.assertRaises(ValueError):
            InputValidator.validate_token_size(16)  # Too small
        
        # Test passphrase validation
        valid_passphrase = InputValidator.validate_passphrase("this_is_a_strong_passphrase_123")
        self.assertEqual(valid_passphrase, "this_is_a_strong_passphrase_123")
        
        with self.assertRaises(ValueError):
            InputValidator.validate_passphrase("weak")  # Too short
    
    @unittest.skipUnless(IMPORTS_AVAILABLE, "Imports not available")
    def test_security_config(self):
        """Test security configuration."""
        # Test Argon2 parameters
        params = SecurityConfig.get_argon2_params()
        self.assertIsInstance(params, dict)
        self.assertIn("time_cost", params)
        self.assertIn("memory_cost", params)
        self.assertIn("parallelism", params)
        
        # Test security validation
        warnings = SecurityConfig.validate_security_level()
        self.assertIsInstance(warnings, list)


class TestPQCIntegration(unittest.TestCase):
    """Test PQC integration if available."""
    
    @unittest.skipUnless(IMPORTS_AVAILABLE and check_pqc_requirements(), "PQC not available")
    def test_pqc_initialization(self):
        """Test that PQC can be initialized."""
        pqc = PostQuantumCrypto()
        self.assertIsNotNone(pqc)
        self.assertIn(pqc.backend, ["rust", "oqs"])
    
    @unittest.skipUnless(IMPORTS_AVAILABLE and check_pqc_requirements(), "PQC not available")
    def test_kem_operations(self):
        """Test basic KEM operations."""
        pqc = PostQuantumCrypto()
        
        # Generate keypair
        pk, sk = pqc.generate_kem_keypair()
        self.assertIsInstance(pk, bytes)
        self.assertIsInstance(sk, bytes)
        self.assertGreater(len(pk), 0)
        self.assertGreater(len(sk), 0)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
