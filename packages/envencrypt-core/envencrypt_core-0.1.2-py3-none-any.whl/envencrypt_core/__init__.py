"""
EnvEncrypt Core - Encryption utilities with optional platform-specific modules

This package provides core encryption functionality with optional modules:
- dpapi: Windows Data Protection API support (Windows only)
- keyring: Cross-platform keyring/password management

Install with extras:
    pip install envencrypt-core[dpapi]     # Windows DPAPI support
    pip install envencrypt-core[keyring]   # Keyring support  
    pip install envencrypt-core[all]       # All available modules
"""

from typing import Dict, Tuple

__version__ = "0.1.0"

# Track which optional modules are available
_available_modules: Dict[str, bool] = {}

# Try to import DPAPI module
try:
    from envencrypt_core import dpapi
    _available_modules['dpapi'] = True
except ImportError:
    dpapi = None
    _available_modules['dpapi'] = False

# Try to import keyring module
try:
    from envencrypt_core import keyring
    _available_modules['keyring'] = True
except ImportError:
    keyring = None
    _available_modules['keyring'] = False


def available_modules() -> Dict[str, bool]:
    """Return a dictionary of available optional modules."""
    return _available_modules.copy()


def require_module(module_name: str) -> None:
    """Raise ImportError if required module is not available."""
    if not _available_modules.get(module_name, False):
        extras_map = {
            'dpapi': 'dpapi',
            'keyring': 'keyring'
        }
        extra = extras_map.get(module_name, module_name)
        raise ImportError(
            f"Module '{module_name}' is not available. "
            f"Install with: pip install envencrypt-core[{extra}]"
        )


# Core functionality that's always available
def get_version() -> str:
    """Get the package version."""
    return __version__


# Convenience functions with helpful error messages
def encrypt_with_dpapi(data: bytes, description: str = "") -> bytes:
    """Encrypt data using Windows DPAPI.
    
    Args:
        data: Data to encrypt
        description: Optional description for the encrypted data
        
    Returns:
        Encrypted data
        
    Raises:
        ImportError: If DPAPI module is not available
    """
    require_module('dpapi')
    if dpapi is None:
        raise ImportError("DPAPI module not available")
    return dpapi.encrypt(data, description)  # type: ignore


def decrypt_with_dpapi(encrypted_data: bytes) -> Tuple[bytes, str]:
    """Decrypt data using Windows DPAPI.
    
    Args:
        encrypted_data: Data to decrypt
        
    Returns:
        Tuple of (decrypted_data, description)
        
    Raises:
        ImportError: If DPAPI module is not available
    """
    require_module('dpapi')
    if dpapi is None:
        raise ImportError("DPAPI module not available")
    return dpapi.decrypt(encrypted_data)  # type: ignore


__all__ = [
    "__version__",
    "dpapi", 
    "keyring",
    "available_modules",
    "require_module", 
    "get_version",
    "encrypt_with_dpapi",
    "decrypt_with_dpapi"
]

