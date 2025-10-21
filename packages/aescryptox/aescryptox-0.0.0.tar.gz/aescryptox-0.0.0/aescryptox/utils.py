import base64, os

def pad(data: bytes, block_size: int = 16) -> bytes:
    """PKCS#7 padding"""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    """Remove PKCS#7 padding"""
    if not data:
        return b""
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16 or pad_len > len(data):
        raise ValueError("Invalid padding or corrupted ciphertext")
    return data[:-pad_len]

def bytes_to_hex(data: bytes) -> str:
    return data.hex()

def hex_to_bytes(data: str) -> bytes:
    return bytes.fromhex(data)

def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

def base64_to_bytes(data: str) -> bytes:
    return base64.b64decode(data)

def random_bytes(length: int) -> bytes:
    """Generate cryptographically secure random bytes."""
    return os.urandom(length)
