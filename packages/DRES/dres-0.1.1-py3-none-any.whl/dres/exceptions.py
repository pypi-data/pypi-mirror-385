"""
Custom exceptions for the DRES library.
"""


class DRESError(Exception):
    """Base exception for all DRES-related errors."""

    pass


class AuthenticationError(DRESError):
    """Raised when HMAC verification fails, indicating a potential message tampering."""

    pass


class InvalidPaddingError(DRESError):
    """Raised when PKCS#7 padding is invalid or malformed."""

    pass


class InvalidPackageError(DRESError):
    """Raised when the encrypted package format is incorrect."""

    pass
