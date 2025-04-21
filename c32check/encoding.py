import re
import binascii

C32_ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
HEX_CHARS = '0123456789abcdef'
C32_CHAR_TO_VALUE = {char: index for index, char in enumerate(C32_ALPHABET)}


def c32normalize(c32input: str) -> str:
    return c32input.upper().replace('O', '0').replace('L', '1').replace('I', '1')


def c32encode(input_hex: str, min_length: int = None) -> str:
    """Encode a hex string into C32 format."""
    if not re.fullmatch(r'[0-9a-fA-F]*', input_hex):
        raise ValueError('Not a hex-encoded string')

    input_hex = input_hex.zfill(len(input_hex) + len(input_hex) % 2)  # Ensure even length

    input_hex = input_hex.lower()
    res = []
    carry = 0

    for i in reversed(range(len(input_hex))):
        if carry < 4:
            current_code = HEX_CHARS.index(input_hex[i]) >> carry
            next_code = HEX_CHARS.index(input_hex[i - 1]) if i != 0 else 0
            next_bits = 1 + carry
            next_low_bits = (next_code % (1 << next_bits)) << (5 - next_bits)
            cur_c32_digit = C32_ALPHABET[current_code + next_low_bits]
            carry = next_bits
            res.insert(0, cur_c32_digit)
        else:
            carry = 0

    c32_leading_zeros = 0
    for ch in res:
        if ch != '0':
            break
        c32_leading_zeros += 1
    res = res[c32_leading_zeros:]

    try:
        zero_prefix = binascii.unhexlify(input_hex).decode('latin1')
        num_leading_zero_bytes = len(re.match(r'^(\x00)*', zero_prefix).group(0))
    except Exception:
        num_leading_zero_bytes = 0

    for _ in range(num_leading_zero_bytes):
        res.insert(0, C32_ALPHABET[0])

    if min_length:
        for _ in range(min_length - len(res)):
            res.insert(0, C32_ALPHABET[0])

    return ''.join(res)


def c32decode(c32input: str, min_length: int = None) -> str:
    """Decode a C32-encoded string into hex."""
    c32input = c32normalize(c32input)
    if not re.fullmatch(f'[{C32_ALPHABET}]*', c32input):
        raise ValueError('Not a c32-encoded string')

    zero_prefix_match = re.match(f'^{C32_ALPHABET[0]}*', c32input)
    num_leading_zero_bytes = len(zero_prefix_match.group(0)) if zero_prefix_match else 0

    res = []
    carry = 0
    carry_bits = 0

    for i in reversed(range(len(c32input))):
        if carry_bits == 4:
            res.insert(0, HEX_CHARS[carry])
            carry_bits = 0
            carry = 0
        current_code = C32_ALPHABET.index(c32input[i]) << carry_bits
        current_value = current_code + carry
        current_hex_digit = HEX_CHARS[current_value % 16]
        carry_bits += 1
        carry = current_value >> 4
        if carry > (1 << carry_bits):
            raise ValueError('Panic error in decoding')
        res.insert(0, current_hex_digit)

    res.insert(0, HEX_CHARS[carry])

    if len(res) % 2 == 1:
        res.insert(0, '0')

    hex_leading_zeros = 0
    for ch in res:
        if ch != '0':
            break
        hex_leading_zeros += 1

    res = res[hex_leading_zeros - (hex_leading_zeros % 2):]
    hex_str = ''.join(res)

    for _ in range(num_leading_zero_bytes):
        hex_str = '00' + hex_str

    if min_length:
        while len(hex_str) < min_length * 2:
            hex_str = '00' + hex_str

    return hex_str


def int_to_c32(value: int) -> str:
    """Convert an integer to a C32Check-encoded string."""
    if value < 0:
        raise ValueError("Value must be non-negative")

    result = []
    while value > 0:
        value, remainder = divmod(value, 32)
        result.append(C32_ALPHABET[remainder])

    return ''.join(reversed(result)) or C32_ALPHABET[0]
