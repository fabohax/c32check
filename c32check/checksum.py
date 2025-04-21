import hashlib
import binascii
from .encoding import int_to_c32, C32_ALPHABET

c32 = C32_ALPHABET

def c32checksum(data_hex: str) -> str:
    data = bytes.fromhex(data_hex)
    data_hash = hashlib.sha256(hashlib.sha256(data).digest()).digest()
    return data_hash[:4].hex()

def double_sha256_checksum(data: bytes) -> bytes:
    """Calculate the double SHA-256 checksum."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]

def c32check_encode(version: int, data_hex: str) -> str:
    if version < 0 or version >= 32:
        raise ValueError("Invalid version (must be between 0 and 31)")

    if not isinstance(data_hex, str) or not all(c in '0123456789abcdefABCDEF' for c in data_hex):
        raise ValueError("Invalid data (not a hex string)")

    data_hex = data_hex.lower()
    if len(data_hex) % 2 != 0:
        data_hex = '0' + data_hex

    version_hex = hex(version)[2:].rjust(2, '0')
    checksum_hex = c32checksum(version_hex + data_hex)
    full_data_hex = data_hex + checksum_hex

    value = int(full_data_hex, 16)
    encoded = int_to_c32(value)

    return c32[version] + encoded

def c32check_decode(c32data: str) -> tuple[int, str]:
    if not c32data or len(c32data) < 3:
        raise ValueError("Invalid c32check string")

    version_char = c32data[0]
    if version_char not in c32:
        raise ValueError("Invalid version character")
    version = c32.index(version_char)

    encoded = c32data[1:]
    value = 0
    for c in encoded:
        if c not in c32:
            raise ValueError(f"Invalid character in c32 data: {c}")
        value = value * 32 + c32.index(c)

    hex_data = hex(value)[2:].rjust(48, '0')
    data_hex = hex_data[:-8]
    checksum_hex = hex_data[-8:]

    version_hex = hex(version)[2:].rjust(2, '0')
    if c32checksum(version_hex + data_hex) != checksum_hex:
        raise ValueError("Invalid c32check string: checksum mismatch")

    return version, data_hex
