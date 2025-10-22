"""
Diffie-Hellman Key Exchange.

This module implements a Diffie-Hellman-style key exchange to establish
a shared secret, providing Perfect Forward Secrecy.
"""

from typing import Tuple

from .util import secure_random_bytes, sha256_hash


class KeyExchange:
    """
    Uses a standard 2048-bit MODP group (from RFC 3526) to perform
    a Diffie-Hellman key exchange.
    """

    # A standard 2048-bit MODP group prime (RFC 3526, Group 14)
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
        "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
        "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
        "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
        "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
        "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
        "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
        16,
    )
    G = 2  # Generator

    @classmethod
    def generate_keypair(cls) -> Tuple[int, int]:
        """Generates a private key and a corresponding public key."""
        # A 32-byte (256-bit) private key is sufficient for security.
        private_key = int.from_bytes(secure_random_bytes(32), "big")
        public_key = pow(cls.G, private_key, cls.P)
        return private_key, public_key

    @classmethod
    def compute_shared_secret(cls, private_key: int, other_public_key: int) -> bytes:
        """Computes the shared secret and hashes it to produce a uniform key."""
        shared_secret_int = pow(other_public_key, private_key, cls.P)
        # The prime P is 2048 bits, which is 256 bytes.
        shared_secret_bytes = shared_secret_int.to_bytes(256, "big")
        return sha256_hash(shared_secret_bytes)
