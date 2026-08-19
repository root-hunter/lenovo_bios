#!/usr/bin/env python3
"""Validate, query, and render the BIOS profiles used to package SREP."""

from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path
import re
import sys
from typing import Any
from uuid import UUID


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"generated", "firmware-verified", "hardware-tested", "deprecated"}
SUPPORTED_STRATEGY = "insyde-h2o-formset-visibility"


class ProfileError(ValueError):
    pass


def require(value: Any, expected: type, field: str) -> Any:
    if not isinstance(value, expected):
        raise ProfileError(f"{field} must be {expected.__name__}")
    return value


def require_string(value: Any, field: str) -> str:
    result = require(value, str, field)
    if not result.strip():
        raise ProfileError(f"{field} must not be empty")
    return result


def string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    items = require(value, list, field)
    if not allow_empty and not items:
        raise ProfileError(f"{field} must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in items):
        raise ProfileError(f"{field} must contain only non-empty strings")
    if len(items) != len(set(items)):
        raise ProfileError(f"{field} contains duplicate values")
    return items


def read_json(path: Path, description: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(f"cannot read {description} {path}: {error}") from error
    return require(data, dict, description)


def load_profile(path: Path) -> tuple[Path, dict[str, Any]]:
    profile_dir = path if path.is_dir() else path.parent
    manifest_path = profile_dir / "profile.json" if path.is_dir() else path
    return profile_dir, read_json(manifest_path, "profile")


def find_strategy(profile_dir: Path, strategy_id: str) -> tuple[Path, dict[str, Any]]:
    if not ID_RE.fullmatch(strategy_id):
        raise ProfileError("strategy must be a safe lowercase identifier")
    for base in (profile_dir, *profile_dir.parents):
        strategy_path = base / "strategies" / f"{strategy_id}.json"
        if strategy_path.is_file():
            return strategy_path, read_json(strategy_path, "strategy")
    raise ProfileError(f"strategy definition not found: {strategy_id}")


def validate_strategy(path: Path, data: dict[str, Any], strategy_id: str) -> None:
    if data.get("schema_version") != 1:
        raise ProfileError(f"{path}: schema_version must be 1")
    if data.get("id") != strategy_id:
        raise ProfileError(f"{path}: strategy id does not match its filename/reference")
    if strategy_id != SUPPORTED_STRATEGY:
        raise ProfileError(f"unsupported strategy renderer: {strategy_id}")

    firmware = require(data.get("firmware"), dict, "strategy.firmware")
    require_string(firmware.get("vendor"), "strategy.firmware.vendor")
    require_string(firmware.get("family"), "strategy.firmware.family")
    layout = require(data.get("record_layout"), dict, "strategy.record_layout")
    expected_layout = {
        "guid_encoding": "uefi-guid-little-endian",
        "visibility_type": "uint32-little-endian",
        "hidden_value": 0,
        "shown_value": 1,
    }
    if layout != expected_layout:
        raise ProfileError(f"{path}: unsupported record_layout")
    string_list(data.get("target_module_candidates"), "target_module_candidates")
    string_list(data.get("launcher_candidates"), "launcher_candidates")
    source = require(data.get("source"), dict, "strategy.source")
    require_string(source.get("project"), "strategy.source.project")
    revision = require_string(source.get("revision"), "strategy.source.revision")
    if not GIT_COMMIT_RE.fullmatch(revision):
        raise ProfileError("strategy.source.revision must be a full lowercase Git commit")
    require_string(source.get("documentation"), "strategy.source.documentation")
    source_url = require_string(source.get("url"), "strategy.source.url")
    if not source_url.startswith("https://"):
        raise ProfileError("strategy.source.url must use HTTPS")


def canonical_guid(value: Any, field: str) -> str:
    text = require_string(value, field)
    try:
        parsed = UUID(text)
    except ValueError as error:
        raise ProfileError(f"{field} is not a valid GUID: {text}") from error
    canonical = str(parsed).upper()
    if text != canonical:
        raise ProfileError(f"{field} must use canonical uppercase form: {canonical}")
    return canonical


def render_config(data: dict[str, Any], strategy: dict[str, Any]) -> str:
    targets = require(data.get("targets"), dict, "targets")
    module = require_string(targets.get("module"), "targets.module")
    launcher = require_string(targets.get("launcher"), "targets.launcher")
    layout = require(strategy.get("record_layout"), dict, "strategy.record_layout")
    hidden = int(layout["hidden_value"]).to_bytes(4, "little").hex().upper()
    shown = int(layout["shown_value"]).to_bytes(4, "little").hex().upper()

    lines = ["Op Loaded", module]
    for index, form_set in enumerate(require(data.get("form_sets"), list, "form_sets")):
        form_set = require(form_set, dict, f"form_sets[{index}]")
        guid = canonical_guid(form_set.get("guid"), f"form_sets[{index}].guid")
        guid_bytes = UUID(guid).bytes_le.hex().upper()
        lines.extend(("Op Patch", "Pattern", guid_bytes + hidden, guid_bytes + shown))
    lines.extend(("Op End", "", "Op LoadFromFV", launcher, "Op Exec", ""))
    return "\n".join(lines)


def validate(path: Path) -> tuple[str, int]:
    profile_dir, data = load_profile(path)
    if data.get("schema_version") != 2:
        raise ProfileError("profile schema_version must be 2")

    profile_id = require_string(data.get("id"), "id")
    if not ID_RE.fullmatch(profile_id):
        raise ProfileError("id must contain lowercase letters, digits, and single hyphens")
    if profile_dir.name != profile_id:
        raise ProfileError(f"profile directory must be named {profile_id}")
    require_string(data.get("display_name"), "display_name")

    platform = require(data.get("platform"), dict, "platform")
    require_string(platform.get("manufacturer"), "platform.manufacturer")
    string_list(platform.get("machine_types"), "platform.machine_types")
    string_list(platform.get("product_names"), "platform.product_names")

    profile_firmware = require(data.get("firmware"), dict, "firmware")
    require_string(profile_firmware.get("vendor"), "firmware.vendor")
    require_string(profile_firmware.get("family"), "firmware.family")
    architecture = require_string(profile_firmware.get("architecture"), "firmware.architecture")
    if architecture != "x86_64":
        raise ProfileError("SREP packaging currently supports only x86_64 profiles")

    compatibility = require(data.get("compatibility"), dict, "compatibility")
    require_string(compatibility.get("bios_family"), "compatibility.bios_family")
    analyzed = string_list(
        compatibility.get("analyzed_versions"),
        "compatibility.analyzed_versions",
        allow_empty=True,
    )
    tested = string_list(
        compatibility.get("hardware_tested_versions"),
        "compatibility.hardware_tested_versions",
        allow_empty=True,
    )

    strategy_id = require_string(data.get("strategy"), "strategy")
    strategy_path, strategy = find_strategy(profile_dir, strategy_id)
    validate_strategy(strategy_path, strategy, strategy_id)
    strategy_firmware = require(strategy.get("firmware"), dict, "strategy.firmware")
    for field in ("vendor", "family"):
        if profile_firmware.get(field) != strategy_firmware.get(field):
            raise ProfileError(f"firmware.{field} does not match the selected strategy")

    targets = require(data.get("targets"), dict, "targets")
    module = require_string(targets.get("module"), "targets.module")
    launcher = require_string(targets.get("launcher"), "targets.launcher")
    if module not in strategy["target_module_candidates"]:
        raise ProfileError("targets.module is not a candidate allowed by the strategy")
    if launcher not in strategy["launcher_candidates"]:
        raise ProfileError("targets.launcher is not a candidate allowed by the strategy")

    form_sets = require(data.get("form_sets"), list, "form_sets")
    if not form_sets:
        raise ProfileError("form_sets must not be empty")
    seen_guids: set[str] = set()
    for index, item in enumerate(form_sets):
        prefix = f"form_sets[{index}]"
        item = require(item, dict, prefix)
        guid = canonical_guid(item.get("guid"), f"{prefix}.guid")
        if guid in seen_guids:
            raise ProfileError(f"duplicate form-set GUID: {guid}")
        seen_guids.add(guid)
        require_string(item.get("name"), f"{prefix}.name")
        if item.get("required") is not True:
            raise ProfileError(f"{prefix}.required must be true for the current renderer")
        require_string(item.get("provenance"), f"{prefix}.provenance")

    status = require_string(data.get("status"), "status")
    if status not in STATUSES:
        raise ProfileError(f"status must be one of: {', '.join(sorted(STATUSES))}")
    if status == "hardware-tested" and not tested:
        raise ProfileError("hardware-tested profiles must list a tested BIOS version")

    evidence = require(data.get("evidence"), list, "evidence")
    known_versions = set(analyzed) | set(tested)
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        item = require(item, dict, prefix)
        version = require_string(item.get("bios_version"), f"{prefix}.bios_version")
        if version not in known_versions:
            raise ProfileError(f"{prefix}.bios_version is not listed under compatibility")
        require_string(item.get("file"), f"{prefix}.file")
        require_string(item.get("type"), f"{prefix}.type")
        digest = require_string(item.get("sha256"), f"{prefix}.sha256")
        if not SHA256_RE.fullmatch(digest):
            raise ProfileError(f"{prefix}.sha256 must be 64 lowercase hexadecimal digits")

    config_name = require_string(data.get("config"), "config")
    readme_name = require_string(data.get("readme"), "readme")
    if Path(config_name).name != config_name or Path(readme_name).name != readme_name:
        raise ProfileError("config and readme must be filenames inside the profile directory")
    config_path = profile_dir / config_name
    readme_path = profile_dir / readme_name
    if not readme_path.is_file() or not readme_path.stat().st_size:
        raise ProfileError(f"missing or empty profile README: {readme_path}")
    try:
        tracked_config = config_path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as error:
        raise ProfileError(f"cannot read generated configuration {config_path}: {error}") from error
    if tracked_config != render_config(data, strategy):
        raise ProfileError(
            f"{config_path} is stale; run: python3 scripts/profile_tool.py sync {profile_dir}"
        )
    return profile_id, len(form_sets)


def discover(profiles_root: Path) -> list[Path]:
    return sorted(path.parent for path in profiles_root.glob("*/profile.json"))


def sync(path: Path) -> tuple[str, Path]:
    profile_dir, data = load_profile(path)
    if data.get("schema_version") != 2:
        raise ProfileError("profile schema_version must be 2")
    strategy_id = require_string(data.get("strategy"), "strategy")
    strategy_path, strategy = find_strategy(profile_dir, strategy_id)
    validate_strategy(strategy_path, strategy, strategy_id)
    config_name = require_string(data.get("config"), "config")
    if Path(config_name).name != config_name:
        raise ProfileError("config must be a filename inside the profile directory")
    output = profile_dir / config_name
    output.write_text(render_config(data, strategy), encoding="ascii")
    profile_id, _ = validate(profile_dir)
    return profile_id, output


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
    render_parser = subparsers.add_parser("render", help="render SREP config to stdout")
    render_parser.add_argument("profile", type=Path)
    sync_parser = subparsers.add_parser("sync", help="regenerate tracked SREP configs")
    sync_parser.add_argument("paths", nargs="+", type=Path)

    args = parser.parse_args()
    try:
        if args.command == "validate":
            for path in args.paths:
                profile_id, count = validate(path)
                print(f"Validated {profile_id}: {count} form-set visibility patch(es)")
        elif args.command == "list":
            profiles = discover(args.profiles_root)
            if not profiles:
                raise ProfileError(f"no profiles found under {args.profiles_root}")
            for profile in profiles:
                profile_id, _ = validate(profile)
                print(profile_id)
        elif args.command == "get":
            _, data = load_profile(args.profile)
            value: Any = data
            for component in args.field.split("."):
                value = require(value, dict, args.field).get(component)
            if not isinstance(value, (str, int, float)):
                raise ProfileError(f"{args.field} is not a scalar value")
            print(value)
        elif args.command == "render":
            profile_dir, data = load_profile(args.profile)
            strategy_id = require_string(data.get("strategy"), "strategy")
            strategy_path, strategy = find_strategy(profile_dir, strategy_id)
            validate_strategy(strategy_path, strategy, strategy_id)
            print(render_config(data, strategy), end="")
        else:
            for path in args.paths:
                profile_id, output = sync(path)
                print(f"Generated {output} for {profile_id}")
    except (OSError, ProfileError) as error:
        print(f"Profile error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
