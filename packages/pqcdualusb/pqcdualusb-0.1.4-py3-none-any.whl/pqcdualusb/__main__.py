"""
Quick sanity CLI for pqcdualusb
===============================

Test that the library can import and show available backends.
"""

import json
import sys
import pqcdualusb
from pqcdualusb.crypto import get_available_backends


def main():
    """Main CLI entry point."""
    print("pqcdualusb Library Status Check")
    print("=" * 40)
    
    # Get backend availability
    info = get_available_backends()
    
    print("\nAvailable backends:")
    print(json.dumps(info, indent=2))
    
    # Check if any PQC backend is available
    has_pqc = info["rust_pqc"] or info["oqs"]
    
    if has_pqc:
        print("\n✅ Post-quantum cryptography available!")
        sys.exit(0)
    else:
        print("\n⚠️  No PQC backend available - classical crypto only")
        print("Install rust-pqc wheel or python-oqs for quantum resistance")
        
        # Test if classical crypto works
        try:
            from pqcdualusb.crypto import PostQuantumCrypto
            pqc = PostQuantumCrypto(allow_fallback=True)
            sk, pk = pqc.generate_kem_keypair()
            print(f"✅ Classical crypto working: {len(sk)}+{len(pk)} byte keys")
            sys.exit(0)
        except Exception as e:
            # Sanitize error - don't expose internal details
            print(f"❌ Cryptography initialization failed")
            import logging
            logging.getLogger(__name__).error(f"Crypto error: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
