#!/usr/bin/env python3
"""Extract and validate the compressed x86 reset image from FCCN21WW."""

from argparse import ArgumentParser
from pathlib import Path
import zlib


ZLIB_OFFSET = 0xF20100
EXPECTED_SIZE = 0x300000


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="FCCN21WW 16 MiB update ROM")
    parser.add_argument("output", type=Path, help="destination for the reset image")
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    if len(rom) != 0x1000000:
        raise SystemExit(f"Unexpected ROM size: {len(rom):#x}; expected 0x1000000")

    try:
        reset_image = zlib.decompress(rom[ZLIB_OFFSET:])
    except zlib.error as error:
        raise SystemExit(f"No valid zlib stream at {ZLIB_OFFSET:#x}: {error}") from error

    if len(reset_image) != EXPECTED_SIZE:
        raise SystemExit(
            f"Unexpected reset image size: {len(reset_image):#x}; "
            f"expected {EXPECTED_SIZE:#x}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(reset_image)

    print(f"Created {args.output} ({len(reset_image):#x} bytes)")
    print(f"Reset vector: {reset_image[-16:].hex(' ')}")


if __name__ == "__main__":
    main()
