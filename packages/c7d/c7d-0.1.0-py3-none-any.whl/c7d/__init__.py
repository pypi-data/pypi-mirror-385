
"""c7d: Cisco Type 7 encoder/decoder.

WARNING: Cisco Type 7 is *not cryptography*. It is simple XOR obfuscation
and should never be used to protect secrets.
"""
from .core import encrypt, decrypt, KEY

__all__ = ["encrypt", "decrypt", "KEY"]
__version__ = "0.1.0"
