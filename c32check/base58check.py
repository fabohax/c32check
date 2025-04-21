from .encoding import int_to_c32, C32_ALPHABET, C32_CHAR_TO_VALUE
from .checksum import double_sha256_checksum
import base58
import binascii
import hashlib

VERSIONS = {
    'mainnet': {
        'p2pkh': 22,  # 'P'
        'p2sh': 20,   # 'M'
    },
    'testnet': {
        'p2pkh': 26,  # 'T'
        'p2sh': 21,   # 'N'
    }
}

ADDR_BITCOIN_TO_STACKS = {
    0: VERSIONS['mainnet']['p2pkh'],
    5: VERSIONS['mainnet']['p2sh'],
    111: VERSIONS['testnet']['p2pkh'],
    196: VERSIONS['testnet']['p2sh'],
}

ADDR_STACKS_TO_BITCOIN = {
    VERSIONS['mainnet']['p2pkh']: 0,
    VERSIONS['mainnet']['p2sh']: 5,
    VERSIONS['testnet']['p2pkh']: 111,
    VERSIONS['testnet']['p2sh']: 196,
}

def c32encode(version: int, data: bytes) -> str:
    if version < 0 or version > 255:
        raise ValueError("Version byte must be between 0 and 255")

    if len(data) != 20:
        raise ValueError("Expected 20-byte data")

    payload = bytes([version]) + data
    checksum = double_sha256_checksum(payload)
    full_data = payload + checksum

    value = int.from_bytes(full_data, byteorder='big')
    encoded = int_to_c32(value)

    leading_zero_bytes = 0
    for b in full_data:
        if b == 0:
            leading_zero_bytes += 1
        else:
            break
    return '0' * leading_zero_bytes + encoded

def c32address(version: int, hash160hex: str) -> str:
    if not isinstance(hash160hex, str) or len(hash160hex) != 40:
        raise ValueError("Invalid argument: not a hash160 hex string")
    data = binascii.unhexlify(hash160hex)
    return 'S' + c32encode(version, data)

def base58check_decode(encoded: str) -> dict:
    decoded = base58.b58decode(encoded)
    prefix = decoded[:1]
    data = decoded[1:-4]
    checksum = decoded[-4:]
    calc_checksum = hashlib.sha256(hashlib.sha256(decoded[:-4]).digest()).digest()[:4]

    if checksum != calc_checksum:
        raise ValueError("Invalid checksum")

    return {
        "prefix": prefix,
        "data": data
    }

def double_sha256_checksum(data: bytes) -> bytes:
    """Calculate the double SHA-256 checksum."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]

def base58check_encode(data: bytes) -> str:
    """Encode data in Base58Check format."""
    checksum = double_sha256_checksum(data)
    return base58.b58encode(data + checksum).decode()

def b58_to_c32(b58_address: str, version: int = -1) -> str:
    addr_info = base58check_decode(b58_address)
    hash160_bytes = addr_info["data"]
    hash160_hex = binascii.hexlify(hash160_bytes).decode()
    addr_version = addr_info["prefix"][0]

    stacks_version = version if version >= 0 else ADDR_BITCOIN_TO_STACKS.get(addr_version, addr_version)
    return c32address(stacks_version, hash160_hex)

def c32_to_b58(c32addr: str, version: int = -1) -> str:
    stacks_version, hash160_hex = c32address_decode(c32addr)
    bitcoin_version = version if version >= 0 else ADDR_STACKS_TO_BITCOIN.get(stacks_version, stacks_version)
    prefix = bytes([bitcoin_version])
    payload = prefix + binascii.unhexlify(hash160_hex)
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return base58.b58encode(payload + checksum).decode()
