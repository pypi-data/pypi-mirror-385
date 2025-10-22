"""
Authentication and license validation modules for HIDENNSIM.
"""

from .license import validate_license, load_license, LicenseError
from .hardware import generate_hardware_fingerprint
from .crypto import verify_signature, decrypt_license

__all__ = [
    "validate_license",
    "load_license",
    "LicenseError",
    "generate_hardware_fingerprint",
    "verify_signature",
    "decrypt_license",
]
