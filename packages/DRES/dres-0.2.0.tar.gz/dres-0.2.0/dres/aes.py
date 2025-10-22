"""
AES-128 Implementation.

This module provides a pure Python implementation of the AES-128 block cipher,
including key expansion and CBC mode of operation.
"""

from typing import List

# AES constants: S-Box, Inverse S-Box, and Round Constant (RCON)
from .resources import INV_S_BOX, RCON, S_BOX
from .util import xor_bytes

BLOCK_SIZE = 16


def _gmul(a: int, b: int) -> int:
    """Multiply two bytes in the Galois Field GF(2^8) used by AES."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit_set:
            a ^= 0x1B  # AES polynomial x^8 + x^4 + x^3 + x + 1
        b >>= 1
    return p


class AESCipher:
    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("AES-128 key must be 16 bytes long.")
        self._round_keys = self._key_expansion(key)

    def _key_expansion(self, key: bytes) -> List[List[int]]:
        key_symbols = list(key)
        w = [key_symbols[i : i + 4] for i in range(0, 16, 4)]
        for i in range(4, 44):
            temp = list(w[i - 1])
            if i % 4 == 0:
                temp = temp[1:] + temp[:1]  # RotWord
                temp = [S_BOX[b] for b in temp]  # SubWord
                temp[0] ^= RCON[i // 4]
            w.append([w[i - 4][j] ^ temp[j] for j in range(4)])
        return [sum(w[i : i + 4], []) for i in range(0, 44, 4)]

    @staticmethod
    def _sub_bytes(state: List[int]) -> List[int]:
        return [S_BOX[b] for b in state]

    @staticmethod
    def _inv_sub_bytes(state: List[int]) -> List[int]:
        return [INV_S_BOX[b] for b in state]

    @staticmethod
    def _shift_rows(state: List[int]) -> List[int]:
        s = list(state)
        return [
            s[0],
            s[5],
            s[10],
            s[15],
            s[4],
            s[9],
            s[14],
            s[3],
            s[8],
            s[13],
            s[2],
            s[7],
            s[12],
            s[1],
            s[6],
            s[11],
        ]

    @staticmethod
    def _inv_shift_rows(state: List[int]) -> List[int]:
        s = list(state)
        return [
            s[0],
            s[13],
            s[10],
            s[7],
            s[4],
            s[1],
            s[14],
            s[11],
            s[8],
            s[5],
            s[2],
            s[15],
            s[12],
            s[9],
            s[6],
            s[3],
        ]

    @staticmethod
    def _mix_columns(state: List[int]) -> List[int]:
        s = list(state)
        for i in range(4):
            c = s[i * 4 : i * 4 + 4]
            s[i * 4 + 0] = _gmul(c[0], 2) ^ _gmul(c[1], 3) ^ c[2] ^ c[3]
            s[i * 4 + 1] = c[0] ^ _gmul(c[1], 2) ^ _gmul(c[2], 3) ^ c[3]
            s[i * 4 + 2] = c[0] ^ c[1] ^ _gmul(c[2], 2) ^ _gmul(c[3], 3)
            s[i * 4 + 3] = _gmul(c[0], 3) ^ c[1] ^ c[2] ^ _gmul(c[3], 2)
        return s

    @staticmethod
    def _inv_mix_columns(state: List[int]) -> List[int]:
        s = list(state)
        for i in range(4):
            c = s[i * 4 : i * 4 + 4]
            s[i * 4 + 0] = (
                _gmul(c[0], 14) ^ _gmul(c[1], 11) ^ _gmul(c[2], 13) ^ _gmul(c[3], 9)
            )
            s[i * 4 + 1] = (
                _gmul(c[0], 9) ^ _gmul(c[1], 14) ^ _gmul(c[2], 11) ^ _gmul(c[3], 13)
            )
            s[i * 4 + 2] = (
                _gmul(c[0], 13) ^ _gmul(c[1], 9) ^ _gmul(c[2], 14) ^ _gmul(c[3], 11)
            )
            s[i * 4 + 3] = (
                _gmul(c[0], 11) ^ _gmul(c[1], 13) ^ _gmul(c[2], 9) ^ _gmul(c[3], 14)
            )
        return s

    @staticmethod
    def _add_round_key(state: List[int], round_key: List[int]) -> List[int]:
        return [s ^ k for s, k in zip(state, round_key)]

    def encrypt_block(self, plaintext_block: bytes) -> bytes:
        state = list(plaintext_block)
        state = self._add_round_key(state, self._round_keys[0])
        for i in range(1, 10):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, self._round_keys[i])
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self._round_keys[10])
        return bytes(state)

    def decrypt_block(self, cipher_block: bytes) -> bytes:
        state = list(cipher_block)
        state = self._add_round_key(state, self._round_keys[10])
        for i in range(9, 0, -1):
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
            state = self._add_round_key(state, self._round_keys[i])
            state = self._inv_mix_columns(state)
        state = self._inv_shift_rows(state)
        state = self._inv_sub_bytes(state)
        state = self._add_round_key(state, self._round_keys[0])
        return bytes(state)

    def encrypt_cbc(self, plaintext: bytes, iv: bytes) -> bytes:
        """Encrypts data using CBC mode."""
        ciphertext = b""
        prev_block = iv
        for i in range(0, len(plaintext), BLOCK_SIZE):
            block = plaintext[i : i + BLOCK_SIZE]
            xored_block = xor_bytes(block, prev_block)
            encrypted_block = self.encrypt_block(xored_block)
            ciphertext += encrypted_block
            prev_block = encrypted_block
        return ciphertext

    def decrypt_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        """Decrypts data using CBC mode."""
        plaintext = b""
        prev_block = iv
        for i in range(0, len(ciphertext), BLOCK_SIZE):
            block = ciphertext[i : i + BLOCK_SIZE]
            decrypted_block = self.decrypt_block(block)
            xored_block = xor_bytes(decrypted_block, prev_block)
            plaintext += xored_block
            prev_block = block
        return plaintext
