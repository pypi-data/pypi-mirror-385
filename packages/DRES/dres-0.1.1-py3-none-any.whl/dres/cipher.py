import hashlib
import hmac

from .aes import AESCipher
from .exceptions import AuthenticationError, InvalidPackageError, InvalidPaddingError
from .key_exchange import KeyExchange
from .util import (
    HKDF,
    pkcs7_pad,
    pkcs7_unpad,
    secure_random_bytes,
    sha256_hash,
    xor_bytes,
)


class DRESCipher:
    """
    The main DRES hybrid encryption system.

    Includes a 'standard' mode (AES-CBC) and an 'academic' mode
    (Danish Obfuscation Layer + AES-CBC).
    """

    # Define key lengths and other constants
    AES_KEY_LEN = 16  # AES-128 key size
    HMAC_KEY_LEN = 32  # SHA-256 recommended key size
    DOL_KEY_LEN = 32  # Custom key for Danish Obfuscation Layer
    IV_LEN = 16  # AES block size for IV
    HMAC_LEN = 32  # SHA-256 output size
    EPH_PUB_KEY_LEN = 256  # 2048 bits for DH public key

    # --- NEW: Your custom "Danish Obfuscation Layer" ---
    def _apply_danish_layer(self, data: bytes, dol_key: bytes) -> bytes:
        """
        Applies (or removes) the custom XOR-based stream cipher.
        This is your unique academic component.
        """
        # Generate the keystream using a simple HASH-PRNG
        keystream = b""
        counter = 0
        while len(keystream) < len(data):
            # Keystream block = HASH(key + counter)
            counter_bytes = counter.to_bytes(4, "big")
            block = sha256_hash(dol_key + counter_bytes)
            keystream += block
            counter += 1

        # Trim keystream to match data length
        keystream = keystream[: len(data)]

        # Apply the XOR
        return xor_bytes(data, keystream)

    def _derive_keys(self, prk: bytes) -> tuple:
        """Derives all necessary keys from the PRK."""
        # We derive one long block of key material
        # AES_KEY (16) + HMAC_KEY (32) + DOL_KEY (32) = 80 bytes
        key_material = HKDF.expand(
            prk, b"dres-keys", self.AES_KEY_LEN + self.HMAC_KEY_LEN + self.DOL_KEY_LEN
        )

        aes_key = key_material[: self.AES_KEY_LEN]
        hmac_key = key_material[self.AES_KEY_LEN : self.AES_KEY_LEN + self.HMAC_KEY_LEN]
        dol_key = key_material[self.AES_KEY_LEN + self.HMAC_KEY_LEN :]

        return aes_key, hmac_key, dol_key

    def encrypt(
        self, plaintext: bytes, recipient_public_key: int, academic_mode: bool = True
    ) -> bytes:
        """
        Encrypts and authenticates data.
        If academic_mode=True, applies the custom Danish Obfuscation Layer first.
        """
        # 1. Generate ephemeral keypair and shared secret
        ephemeral_private, ephemeral_public = KeyExchange.generate_keypair()
        shared_secret = KeyExchange.compute_shared_secret(
            ephemeral_private, recipient_public_key
        )

        # 2. Derive all three keys
        eph_pub_bytes = ephemeral_public.to_bytes(self.EPH_PUB_KEY_LEN, "big")
        prk = HKDF.extract(salt=eph_pub_bytes, ikm=shared_secret)
        aes_key, hmac_key, dol_key = self._derive_keys(prk)

        # 3. --- YOUR UNIQUE TOUCH ---
        # Apply the custom "Danish Obfuscation Layer" if in academic mode
        if academic_mode:
            plaintext = self._apply_danish_layer(plaintext, dol_key)

        # 4. Encrypt using standard AES-CBC
        aes_cipher = AESCipher(aes_key)
        iv = secure_random_bytes(self.IV_LEN)
        padded_plaintext = pkcs7_pad(plaintext)
        ciphertext = aes_cipher.encrypt_cbc(padded_plaintext, iv)

        # 5. Compute the HMAC tag (Encrypt-then-MAC)
        mac = hmac.new(hmac_key, eph_pub_bytes + iv + ciphertext, hashlib.sha256)
        hmac_tag = mac.digest()

        # 6. Assemble the final package.
        # We must add a flag to tell the recipient which mode was used.
        mode_flag = b"\x01" if academic_mode else b"\x00"
        return mode_flag + eph_pub_bytes + iv + hmac_tag + ciphertext

    def decrypt(self, package: bytes, private_key: int) -> bytes:
        """
        Verifies and decrypts a package.
        Automatically detects if the academic mode was used.
        """
        # 1. Deconstruct the package
        try:
            mode_flag = package[0:1]
            eph_pub_bytes = package[1 : 1 + self.EPH_PUB_KEY_LEN]
            iv_start = 1 + self.EPH_PUB_KEY_LEN
            tag_start = iv_start + self.IV_LEN
            cipher_start = tag_start + self.HMAC_LEN

            iv = package[iv_start:tag_start]
            received_tag = package[tag_start:cipher_start]
            ciphertext = package[cipher_start:]

            academic_mode = mode_flag == b"\x01"
            ephemeral_public_key = int.from_bytes(eph_pub_bytes, "big")
        except (IndexError, TypeError):
            raise InvalidPackageError(
                "The encrypted package has an invalid format or length."
            )

        # 2. Re-compute the shared secret
        shared_secret = KeyExchange.compute_shared_secret(
            private_key, ephemeral_public_key
        )

        # 3. Re-derive all three keys
        prk = HKDF.extract(salt=eph_pub_bytes, ikm=shared_secret)
        aes_key, hmac_key, dol_key = self._derive_keys(prk)

        # 4. Verify the HMAC tag BEFORE decrypting
        mac = hmac.new(hmac_key, eph_pub_bytes + iv + ciphertext, hashlib.sha256)
        expected_tag = mac.digest()

        if not hmac.compare_digest(received_tag, expected_tag):
            raise AuthenticationError(
                "Authentication failed! The message may have been tampered with."
            )

        # 5. HMAC is valid, proceed to decrypt AES
        aes_cipher = AESCipher(aes_key)
        decrypted_padded = aes_cipher.decrypt_cbc(ciphertext, iv)

        # 6. Remove the PKCS#7 padding
        decrypted = pkcs7_unpad(decrypted_padded)

        # 7. --- YOUR UNIQUE TOUCH (Reversed) ---
        # If academic mode was used, remove the obfuscation layer
        if academic_mode:
            decrypted = self._apply_danish_layer(decrypted, dol_key)

        return decrypted
