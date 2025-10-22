"""
DRES - A Hybrid Encryption Library

This package provides a pure-Python implementation of a hybrid encryption
system, combining Diffie-Hellman key exchange, AES-128-CBC, and HMAC-SHA256.

Warning: This library is for educational purposes and has not been
audited. DO NOT use it for real-world sensitive data.
"""

__version__ = "0.1.0"
__author__ = "Danish"

from .cipher import DRESCipher
from .exceptions import (
    AuthenticationError,
    DRESError,
    InvalidPackageError,
    InvalidPaddingError,
)
from .key_exchange import KeyExchange

__all__ = [
    "DRESCipher",
    "KeyExchange",
    "DRESError",
    "AuthenticationError",
    "InvalidPackageError",
    "InvalidPaddingError",
]
