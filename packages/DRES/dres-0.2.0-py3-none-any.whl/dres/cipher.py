"""
The main DRESCipher implementation.

This module contains the core logic for the DRES hybrid encryption system.
It features a custom-designed mode of operation called
"Evolving-Key Chaining" (EKC).
"""

import hmac
import hashlib

from .aes import AESCipher
from .key_exchange import KeyExchange
from .util import (
    HKDF,
    pkcs7_pad,
    pkcs7_unpad,
    secure_random_bytes,
    xor_bytes,
)
from .exceptions import AuthenticationError, InvalidPackageError, InvalidPaddingError


class DRESCipher:
    """
    The main DRES hybrid encryption system, featuring a novel
    "Evolving-Key Chaining" (EKC) mode.
    """

    # --- Key Lengths & Constants ---
    # Key for the EKC block-by-block derivation
    CHAIN_KEY_LEN = 32
    # Key for the final, top-level HMAC authentication
    HMAC_KEY_LEN = 32
    # AES-128 key length
    AES_KEY_LEN = 16
    # AES block size / IV length
    IV_LEN = 16
    # SHA-256 output length
    HMAC_LEN = 32
    # Diffie-Hellman public key length
    EPH_PUB_KEY_LEN = 256

    def _derive_keys(self, prk: bytes) -> tuple:
        """
        Derives all necessary keys from the HKDF's Pseudorandom Key (PRK).
        """
        # We derive one long block of key material
        # CHAIN_KEY (32) + HMAC_KEY (32) = 64 bytes
        key_material = HKDF.expand(
            prk,
            b"dres-ekc-keys",
            self.CHAIN_KEY_LEN + self.HMAC_KEY_LEN,
        )

        chain_key = key_material[: self.CHAIN_KEY_LEN]
        hmac_key = key_material[self.CHAIN_KEY_LEN :]

        return chain_key, hmac_key

    def encrypt(self, plaintext: bytes, recipient_public_key: int) -> bytes:
        """
        Encrypts and authenticates data using the Evolving-Key Chaining (EKC) mode.

        Returns:
            A single bytes package:
            [ephemeral_public_key(256) || iv(16) || hmac_tag(32) || ciphertext]
        """
        # 1. Generate ephemeral keypair and shared secret
        ephemeral_private, ephemeral_public = KeyExchange.generate_keypair()
        shared_secret = KeyExchange.compute_shared_secret(
            ephemeral_private, recipient_public_key
        )

        # 2. Derive the Chain Key and the final HMAC Key
        eph_pub_bytes = ephemeral_public.to_bytes(self.EPH_PUB_KEY_LEN, "big")
        prk = HKDF.extract(salt=eph_pub_bytes, ikm=shared_secret)
        chain_key, hmac_key = self._derive_keys(prk)

        # 3. Pad the plaintext
        padded_plaintext = pkcs7_pad(plaintext, block_size=self.IV_LEN)
        iv = secure_random_bytes(self.IV_LEN)

        # --- 4. Evolving-Key Chaining (EKC) Encryption ---
        ciphertext = b""
        # The first block is chained with the IV
        prev_ciphertext_block = iv

        for i in range(0, len(padded_plaintext), self.IV_LEN):
            # 4a. Derive the unique key for this block
            block_key = hmac.new(
                chain_key, prev_ciphertext_block, hashlib.sha256
            ).digest()[: self.AES_KEY_LEN]

            # 4b. Instantiate AES cipher with the *new* key
            aes_cipher = AESCipher(block_key)

            # 4c. Get the current plaintext block
            plaintext_block = padded_plaintext[i : i + self.IV_LEN]

            # 4d. Chain the plaintext (like CBC)
            xored_block = xor_bytes(plaintext_block, prev_ciphertext_block)

            # 4e. Encrypt the block
            encrypted_block = aes_cipher.encrypt_block(xored_block)

            # 4f. Append to ciphertext and update the chain
            ciphertext += encrypted_block
            prev_ciphertext_block = encrypted_block
        # --- End of EKC Loop ---

        # 5. Compute the final HMAC tag (Encrypt-then-MAC)
        # The tag covers the public key, IV, and the *entire* new ciphertext
        mac = hmac.new(hmac_key, eph_pub_bytes + iv + ciphertext, hashlib.sha256)
        hmac_tag = mac.digest()

        # 6. Assemble the final package
        return eph_pub_bytes + iv + hmac_tag + ciphertext

    def decrypt(self, package: bytes, private_key: int) -> bytes:
        """
        Verifies and decrypts a package encrypted with the EKC mode.
        """
        # 1. Deconstruct the package
        try:
            eph_pub_bytes = package[: self.EPH_PUB_KEY_LEN]
            iv = package[self.EPH_PUB_KEY_LEN : self.EPH_PUB_KEY_LEN + self.IV_LEN]
            received_tag = package[
                self.EPH_PUB_KEY_LEN
                + self.IV_LEN : self.EPH_PUB_KEY_LEN
                + self.IV_LEN
                + self.HMAC_LEN
            ]
            ciphertext = package[self.EPH_PUB_KEY_LEN + self.IV_LEN + self.HMAC_LEN :]

            if len(ciphertext) % self.IV_LEN != 0:
                raise InvalidPackageError(
                    "Ciphertext is not a multiple of the block size."
                )

            ephemeral_public_key = int.from_bytes(eph_pub_bytes, "big")
        except (IndexError, TypeError, ValueError):
            raise InvalidPackageError(
                "The encrypted package has an invalid format or length."
            )

        # 2. Re-compute the shared secret
        shared_secret = KeyExchange.compute_shared_secret(
            private_key, ephemeral_public_key
        )

        # 3. Re-derive the Chain Key and HMAC Key
        prk = HKDF.extract(salt=eph_pub_bytes, ikm=shared_secret)
        chain_key, hmac_key = self._derive_keys(prk)

        # 4. Verify the final HMAC tag BEFORE decrypting
        expected_tag = hmac.new(
            hmac_key, eph_pub_bytes + iv + ciphertext, hashlib.sha256
        ).digest()

        if not hmac.compare_digest(received_tag, expected_tag):
            raise AuthenticationError(
                "Authentication failed! The message may have been tampered with."
            )

        # --- 5. Evolving-Key Chaining (EKC) Decryption ---
        # HMAC is valid, we can now decrypt.
        padded_plaintext = b""
        # The first block is chained with the IV
        prev_ciphertext_block = iv

        for i in range(0, len(ciphertext), self.IV_LEN):
            # 5a. Derive the unique key for this block
            block_key = hmac.new(
                chain_key, prev_ciphertext_block, hashlib.sha256
            ).digest()[: self.AES_KEY_LEN]

            # 5b. Instantiate AES cipher with the *new* key
            aes_cipher = AESCipher(block_key)

            # 5c. Get the current ciphertext block
            ciphertext_block = ciphertext[i : i + self.IV_LEN]

            # 5d. Decrypt the block
            decrypted_block = aes_cipher.decrypt_block(ciphertext_block)

            # 5e. Reverse the plaintext chain (like CBC)
            xored_block = xor_bytes(decrypted_block, prev_ciphertext_block)

            # 5f. Append to plaintext and update the chain
            padded_plaintext += xored_block
            prev_ciphertext_block = ciphertext_block
        # --- End of EKC Loop ---

        # 6. Remove the PKCS#7 padding
        try:
            return pkcs7_unpad(padded_plaintext, block_size=self.IV_LEN)
        except InvalidPaddingError as e:
            # Re-raise as an AuthenticationError.
            # A padding error in an authenticated scheme should be treated
            # as a failed authentication, as it's a sign of a malformed package.
            raise AuthenticationError(f"Decryption failed: {e}")
