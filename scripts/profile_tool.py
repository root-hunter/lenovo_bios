#!/usr/bin/env python3
"""Validate and query the BIOS profiles used to package SREP."""

from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path
import re
import sys
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_PATTERN_RE = re.compile(r"^[0-9A-Fa-f]{40}$")
STATUSES = {"generated", "firmware-verified", "hardware-tested", "deprecated"}


class ProfileError(ValueError):
    pass


def require(value: Any, expected: type, field: str) -> Any:
    if not isinstance(value, expected):
        raise ProfileError(f"{field} must be {expected.__name__}")
    return value


def nonempty_strings(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    items = require(value, list, field)
    if not allow_empty and not items:
        raise ProfileError(f"{field} must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in items):
        raise ProfileError(f"{field} must contain only non-empty strings")
    if len(items) != len(set(items)):
        raise ProfileError(f"{field} contains duplicate values")
    return items


def load_profile(path: Path) -> tuple[Path, dict[str, Any]]:
    profile_dir = path if path.is_dir() else path.parent
    manifest_path = profile_dir / "profile.json" if path.is_dir() else path
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(f"cannot read {manifest_path}: {error}") from error
    return profile_dir, require(data, dict, "profile")


def validate_srep_config(path: Path, module: str, launcher: str) -> int:
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as error:
        raise ProfileError(f"cannot read {path}: {error}") from error

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    patterns = [line.upper() for line in lines if HEX_PATTERN_RE.fullmatch(line)]
    if not patterns or len(patterns) % 2:
        raise ProfileError(f"{path} must contain complete search/replacement pattern pairs")
    pattern_markers = [index for index, line in enumerate(lines) if line == "Pattern"]
    if len(pattern_markers) != len(patterns) // 2:
        raise ProfileError(f"{path} must have one Pattern marker per pattern pair")
    for pair_number, line_index in enumerate(pattern_markers, start=1):
        if line_index + 2 >= len(lines) or not all(
            HEX_PATTERN_RE.fullmatch(line) for line in lines[line_index + 1 : line_index + 3]
        ):
            raise ProfileError(
                f"Pattern marker {pair_number} must be followed by search and replacement bytes"
            )

    originals: list[str] = []
    for index in range(0, len(patterns), 2):
        original, replacement = patterns[index : index + 2]
        if original[:-8] != replacement[:-8]:
            raise ProfileError(f"pattern pair {index // 2 + 1} changes the form-set GUID")
        if not original.endswith("00000000") or not replacement.endswith("01000000"):
            raise ProfileError(
                f"pattern pair {index // 2 + 1} must change only hidden 0 to shown 1"
            )
        originals.append(original)
    if len(originals) != len(set(originals)):
        raise ProfileError(f"{path} contains duplicate search patterns")

    required_fragments = (
        "Op Loaded",
        module,
        "Op LoadFromFV",
        launcher,
        "Op Exec",
    )
    for fragment in required_fragments:
        if fragment not in lines:
            raise ProfileError(f"{path} is missing required line: {fragment}")
    return len(originals)


def validate(path: Path) -> tuple[str, int]:
    profile_dir, data = load_profile(path)
    if data.get("schema_version") != 1:
        raise ProfileError("schema_version must be 1")

    profile_id = require(data.get("id"), str, "id")
    if not ID_RE.fullmatch(profile_id):
        raise ProfileError("id must contain lowercase letters, digits, and single hyphens")
    if profile_dir.name != profile_id:
        raise ProfileError(f"profile directory must be named {profile_id}")
    require(data.get("display_name"), str, "display_name")

    platform = require(data.get("platform"), dict, "platform")
    require(platform.get("manufacturer"), str, "platform.manufacturer")
    nonempty_strings(platform.get("machine_types"), "platform.machine_types")
    nonempty_strings(platform.get("product_names"), "platform.product_names")

    compatibility = require(data.get("compatibility"), dict, "compatibility")
    require(compatibility.get("bios_family"), str, "compatibility.bios_family")
    analyzed = nonempty_strings(
        compatibility.get("analyzed_versions"),
        "compatibility.analyzed_versions",
        allow_empty=True,
    )
    tested = nonempty_strings(
        compatibility.get("hardware_tested_versions"),
        "compatibility.hardware_tested_versions",
        allow_empty=True,
    )

    patch = require(data.get("patch"), dict, "patch")
    module = require(patch.get("module"), str, "patch.module")
    launcher = require(patch.get("launcher"), str, "patch.launcher")

    status = require(data.get("status"), str, "status")
    if status not in STATUSES:
        raise ProfileError(f"status must be one of: {', '.join(sorted(STATUSES))}")
    if status == "hardware-tested" and not tested:
        raise ProfileError("hardware-tested profiles must list a tested BIOS version")

    evidence = require(data.get("evidence"), list, "evidence")
    known_versions = set(analyzed) | set(tested)
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        item = require(item, dict, prefix)
        version = require(item.get("bios_version"), str, f"{prefix}.bios_version")
        if version not in known_versions:
            raise ProfileError(f"{prefix}.bios_version is not listed under compatibility")
        require(item.get("file"), str, f"{prefix}.file")
        require(item.get("type"), str, f"{prefix}.type")
        digest = require(item.get("sha256"), str, f"{prefix}.sha256")
        if not SHA256_RE.fullmatch(digest):
            raise ProfileError(f"{prefix}.sha256 must be 64 lowercase hexadecimal digits")

    config_name = require(data.get("config"), str, "config")
    readme_name = require(data.get("readme"), str, "readme")
    if Path(config_name).name != config_name or Path(readme_name).name != readme_name:
        raise ProfileError("config and readme must be filenames inside the profile directory")
    config_path = profile_dir / config_name
    readme_path = profile_dir / readme_name
    if not readme_path.is_file() or not readme_path.stat().st_size:
        raise ProfileError(f"missing or empty profile README: {readme_path}")
    pattern_count = validate_srep_config(config_path, module, launcher)
    return profile_id, pattern_count


def discover(profiles_root: Path) -> list[Path]:
    return sorted(path.parent for path in profiles_root.glob("*/profile.json"))


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate profiles")
    validate_parser.add_argument("paths", nargs="+", type=Path)

    list_parser = subparsers.add_parser("list", help="list valid profile IDs")
    list_parser.add_argument("profiles_root", type=Path)

    get_parser = subparsers.add_parser("get", help="print a manifest value")
    get_parser.add_argument("profile", type=Path)
    get_parser.add_argument("field", help="dot-separated field name")

    args = parser.parse_args()
    try:
        if args.command == "validate":
            paths = args.paths
            for path in paths:
                profile_id, count = validate(path)
                print(f"Validated {profile_id}: {count} visibility pattern(s)")
        elif args.command == "list":
            profiles = discover(args.profiles_root)
            if not profiles:
                raise ProfileError(f"no profiles found under {args.profiles_root}")
            for profile in profiles:
                profile_id, _ = validate(profile)
                print(profile_id)
        else:
            _, data = load_profile(args.profile)
            value: Any = data
            for component in args.field.split("."):
                value = require(value, dict, args.field).get(component)
            if not isinstance(value, (str, int, float)):
                raise ProfileError(f"{args.field} is not a scalar value")
            print(value)
    except ProfileError as error:
        print(f"Profile error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
