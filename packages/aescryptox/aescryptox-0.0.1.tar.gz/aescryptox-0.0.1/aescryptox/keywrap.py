# keywrap.py
"""
AES Key Wrap (RFC 3394) and Unwrap implementation in pure Python.
Provides secure wrapping/unwrapping of cryptographic keys.
"""

from .aes import AES
from .modes import AESMode

DEFAULT_IV = b"\xA6\xA6\xA6\xA6\xA6\xA6\xA6\xA6"

class AESKeyWrap:
    @staticmethod
    def wrap(kek: bytes, plaintext: bytes, iv: bytes = DEFAULT_IV) -> bytes:
        """
        Wrap (encrypt) a key using AES Key Wrap (RFC 3394).
        kek: Key Encryption Key (16, 24, or 32 bytes)
        plaintext: Key data (must be multiple of 8 bytes, >=16)
        Returns ciphertext (wrapped key)
        """
        if len(plaintext) % 8 != 0 or len(plaintext) < 16:
            raise ValueError("Plaintext length must be a multiple of 8 bytes and at least 16 bytes.")
        
        n = len(plaintext) // 8
        R = [plaintext[i*8:(i+1)*8] for i in range(n)]
        A = bytearray(iv)
        aes = AES(kek, AESMode.ECB)

        # 6 rounds * n blocks
        for j in range(6):
            for i in range(1, n + 1):
                B = aes.encrypt_block(A + R[i - 1])
                t = (n * j + i)
                t_bytes = t.to_bytes(8, 'big')
                A = bytearray(x ^ y for x, y in zip(B[:8], t_bytes))
                R[i - 1] = B[8:]
        
        return bytes(A) + b''.join(R)

    @staticmethod
    def unwrap(kek: bytes, ciphertext: bytes, iv: bytes = DEFAULT_IV) -> bytes:
        """
        Unwrap (decrypt) a key using AES Key Unwrap (RFC 3394).
        kek: Key Encryption Key (16, 24, or 32 bytes)
        ciphertext: Wrapped key
        Returns plaintext key
        """
        if len(ciphertext) % 8 != 0 or len(ciphertext) < 24:
            raise ValueError("Ciphertext length must be a multiple of 8 bytes and at least 24 bytes.")
        
        n = (len(ciphertext) // 8) - 1
        A = bytearray(ciphertext[:8])
        R = [ciphertext[8 + 8*i:16 + 8*i] for i in range(n)]
        aes = AES(kek, AESMode.ECB)

        # Inverse operation: 6 rounds * n blocks
        for j in range(5, -1, -1):
            for i in range(n, 0, -1):
                t = (n * j + i)
                t_bytes = t.to_bytes(8, 'big')
                A_xor_t = bytes(x ^ y for x, y in zip(A, t_bytes))
                B = aes.decrypt_block(A_xor_t + R[i - 1])
                A = bytearray(B[:8])
                R[i - 1] = B[8:]
        
        if bytes(A) != iv:
            raise ValueError("Integrity check failed: invalid AES key unwrap (IV mismatch).")
        
        return b''.join(R)
