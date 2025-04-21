import hashlib
import binascii
from .encoding import int_to_c32, C32_ALPHABET
from .base58check import base58check_decode, base58check_encode, ADDR_BITCOIN_TO_STACKS, ADDR_STACKS_TO_BITCOIN

c32 = C32_ALPHABET

def c32checksum(data_hex: str) -> str:
    data = bytes.fromhex(data_hex)
    data_hash = hashlib.sha256(hashlib.sha256(data).digest()).digest()
    return data_hash[:4].hex()

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

def c32address(version: int, hash160hex: str) -> str:
    """Generate a C32Check address from a version and hash160 hex string."""
    if not isinstance(hash160hex, str) or len(hash160hex) != 40:
        raise ValueError("Invalid argument: not a hash160 hex string")
    data = binascii.unhexlify(hash160hex)
    return c32check_encode(version, data.hex())

def c32address_decode(c32addr: str) -> tuple:
    """Decode a C32Check address into its version and hash160 hex string."""
    if len(c32addr) <= 5:
        raise ValueError("Invalid c32 address: too short")
    if not c32addr.startswith("S"):
        raise ValueError("Invalid c32 address: must start with 'S'")

    c32_body = c32addr[1:]
    value = 0
    for c in c32_body:
        if c not in C32_ALPHABET:
            raise ValueError(f"Invalid character in c32 address: {c}")
        value = value * 32 + C32_ALPHABET.index(c)

    full_data = value.to_bytes((value.bit_length() + 7) // 8, 'big')

    # Add leading zeros
    num_leading_zeros = len(c32_body) - len(c32_body.lstrip('0'))
    full_data = b'\x00' * num_leading_zeros + full_data

    if len(full_data) < 25:
        raise ValueError("Invalid c32 data length")

    payload, checksum = full_data[:-4], full_data[-4:]
    calc_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    if checksum != calc_checksum:
        raise ValueError("Checksum mismatch")

    version = payload[0]
    data = payload[1:]
    if len(data) != 20:
        raise ValueError("Invalid hash160 length")

    return version, binascii.hexlify(data).decode()

def b58_to_c32(b58_address: str) -> str:
    """Convert a Base58Check address to a C32Check address."""
    addr_info = base58check_decode(b58_address)
    hash160_bytes = addr_info["data"]
    hash160_hex = binascii.hexlify(hash160_bytes).decode()
    addr_version = addr_info["prefix"][0]

    stacks_version = ADDR_BITCOIN_TO_STACKS.get(addr_version, addr_version)
    return c32address(stacks_version, hash160_hex)

def c32_to_b58(c32_address: str) -> str:
    """Convert a C32Check address to a Base58Check address."""
    stacks_version, hash160_hex = c32address_decode(c32_address)
    bitcoin_version = ADDR_STACKS_TO_BITCOIN.get(stacks_version, stacks_version)
    prefix = bytes([bitcoin_version])
    payload = prefix + binascii.unhexlify(hash160_hex)
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return base58check_encode(payload + checksum)
