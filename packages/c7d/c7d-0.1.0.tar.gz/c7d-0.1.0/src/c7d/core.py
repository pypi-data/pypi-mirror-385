
from __future__ import annotations

KEY = 'dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87'  # length 53

class C7DValueError(ValueError):
    """Raised when input values are invalid for c7 encoding/decoding."""


def decrypt(x: str) -> str:
    """Decode a Cisco Type 7 string to plaintext.

    Args:
        x: Type 7 string. First two chars are a decimal seed (00-99),
           followed by an even number of hex digits.

    Returns:
        The decoded plaintext string.

    Raises:
        C7DValueError: if the input format is invalid.
    """
    if not isinstance(x, str):
        raise C7DValueError("x must be a string")
    if len(x) < 2:
        raise C7DValueError("input too short: need at least a 2-digit seed")
    seed_str = x[:2]
    if not seed_str.isdigit():
        raise C7DValueError("first two characters must be decimal digits (seed)")
    body = x[2:]
    if len(body) % 2 != 0:
        raise C7DValueError("hex body length must be even")

    seed = int(seed_str)
    out_chars = []
    for i in range(0, len(body), 2):
        byte_hex = body[i:i+2]
        try:
            ciph_byte = int(byte_hex, 16)
        except ValueError as e:
            raise C7DValueError(f"invalid hex byte: {byte_hex}") from e
        pos = i // 2  # 0-based position within the hex body
        key_ch = KEY[(seed + pos) % len(KEY)]
        plain = ciph_byte ^ ord(key_ch)
        out_chars.append(chr(plain))
    return ''.join(out_chars)


def encrypt(plain: str, seed: int = 0) -> str:
    """Encode plaintext into Cisco Type 7 format.

    Args:
        plain: The plaintext to obfuscate.
        seed:  Decimal seed in range 0..99 (will be used as-is, not modulo).

    Returns:
        A Type 7 string: two-digit decimal seed + uppercase hex bytes.

    Raises:
        C7DValueError: if the seed is out of range or plain is not str.
    """
    if not isinstance(plain, str):
        raise C7DValueError("plain must be a string")
    if not (0 <= seed <= 99):
        raise C7DValueError("seed must be an integer between 0 and 99 inclusive")

    seed_str = f"{seed:02d}"
    out_hex = []
    for i, ch in enumerate(plain):
        key_ch = KEY[(seed + i) % len(KEY)]
        ciph = ord(ch) ^ ord(key_ch)
        out_hex.append(f"{ciph:02X}")
    return seed_str + ''.join(out_hex)
