"""
Cryptographic Utilities.

This module provides helper functions and classes used throughout the DRES library,
including HKDF, hashing, padding, and secure random number generation.
"""

import hashlib
import hmac
import secrets

from .exceptions import InvalidPaddingError


def secure_random_bytes(n: int) -> bytes:
    """Generates cryptographically secure random bytes."""
    return secrets.token_bytes(n)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XORs two byte strings of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))


def sha256_hash(data: bytes) -> bytes:
    """Computes the SHA-256 hash of the given data."""
    return hashlib.sha256(data).digest()


class HKDF:
    """
    A simple implementation of the HKDF standard (RFC 5869).
    """

    @staticmethod
    def extract(salt: bytes, ikm: bytes) -> bytes:
        """HKDF-Extract: Creates a fixed-length pseudorandom key (PRK)."""
        return hmac.new(salt, ikm, hashlib.sha256).digest()

    @staticmethod
    def expand(prk: bytes, info: bytes, length: int) -> bytes:
        """HKDF-Expand: Expands the PRK into the desired number of bytes."""
        t = b""
        okm = b""
        i = 1
        # Handle cases where length is > 32 bytes (one hash output)
        while len(okm) < length:
            # We now use a counter in the info tag for multiple blocks
            info_with_counter = info + i.to_bytes(1, "big")
            t = hmac.new(prk, t + info_with_counter, hashlib.sha256).digest()
            okm += t
            i += 1
        return okm[:length]


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    """Applies PKCS#7 padding to data."""
    if block_size < 1 or block_size > 255:
        raise ValueError("Block size must be between 1 and 255.")
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    """Removes PKCS#7 padding from data."""
    if not data:
        return b""
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise InvalidPaddingError("Invalid padding length.")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise InvalidPaddingError("Padding bytes are incorrect.")
    return data[:-pad_len]
