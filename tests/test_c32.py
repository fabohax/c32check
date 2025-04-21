import pytest
from c32check import (
    c32address,
    c32address_decode,
    b58_to_c32,
    c32_to_b58,
    c32check_encode,
    c32check_decode,
    base58check_encode,
    base58check_decode,
)

def test_c32address_roundtrip():
    hash160 = '751e76e8199196d454941c45d1b3a323f1433bd6'
    version = 22
    c32addr = c32address(version, hash160)
    decoded_version, decoded_hash = c32address_decode(c32addr)
    assert version == decoded_version
    assert hash160 == decoded_hash

def test_b58_to_c32_and_back():
    btc_addr = '1BoatSLRHtKNngkdXEeobR76b53LETtpyT'
    c32addr = b58_to_c32(btc_addr)
    roundtrip = c32_to_b58(c32addr)
    assert btc_addr == roundtrip

def test_b58_to_c32_invalid():
    with pytest.raises(ValueError):
        b58_to_c32("invalid_base58")

def test_c32_to_b58_invalid():
    with pytest.raises(ValueError):
        c32_to_b58("invalid_c32")

def test_c32check_direct_encode_decode():
    hash160 = '751e76e8199196d454941c45d1b3a323f1433bd6'
    version = 22
    encoded = c32check_encode(version, hash160)
    decoded_version, decoded_data = c32check_decode(encoded)
    assert decoded_version == version
    assert decoded_data == hash160

def test_base58check_encode_decode():
    hash160 = '751e76e8199196d454941c45d1b3a323f1433bd6'
    prefix = b'\x00'
    encoded = base58check_encode(hash160, prefix)
    decoded = base58check_decode(encoded)
    assert decoded['prefix'] == prefix
    assert decoded['data'].hex() == hash160
