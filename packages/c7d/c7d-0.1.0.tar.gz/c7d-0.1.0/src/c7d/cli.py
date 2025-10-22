from __future__ import annotations

import argparse
import sys

from .core import C7DValueError, decrypt, encrypt


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="c7d",
        description=(
            "Encode/decode Cisco Type 7 strings.\n\n"
            "WARNING: Type 7 is insecure obfuscation, not encryption."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_dec = sub.add_parser("decrypt", help="Decrypt a Type 7 string to plaintext")
    p_dec.add_argument("cipher", help="Type 7 string, e.g. 060506324F41")

    p_enc = sub.add_parser("encrypt", help="Encrypt plaintext into Type 7 format")
    p_enc.add_argument("plain", help="Plaintext to encode")
    p_enc.add_argument(
        "--seed", type=int, default=0, help="Decimal seed 0..99 (default: 0)"
    )

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(argv)
    try:
        if ns.cmd == "decrypt":
            print(decrypt(ns.cipher))
        elif ns.cmd == "encrypt":
            print(encrypt(ns.plain, seed=ns.seed))
        else:
            parser.error("unknown command")
            return 2
        return 0
    except C7DValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
