#!/usr/bin/env python3
"""
override.py — Apply ChatFort brand and feature overrides to upstream files.

Reads brand_config.json for string replacements, Icon Composer bundle copies,
and preview icon file copies. Also auto-discovers YAML config files in the
configs/ directory for modular, feature-specific overrides.

Application order:
  1. brand_config.json (existing branding — always first)
  2. configs/*.yaml    (feature overrides — alphabetical order)

Usage:
    python3 override.py              # default: --dry-run
    python3 override.py --dry-run    # show colored diff, write nothing
    python3 override.py --apply      # show colored diff, then write changes
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRAND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BRAND_DIR.parent.parent
CONFIG_PATH = BRAND_DIR / "brand_config.json"
CONFIGS_DIR = BRAND_DIR / "configs"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Minimal YAML parser (stdlib only — no PyYAML dependency)
# ---------------------------------------------------------------------------
# Supports the subset used by override configs: scalars, lists, dicts,
# multi-line strings via | (literal block) and > (folded block), and
# inline flow sequences/mappings. Enough for our YAML config schema.

def _yaml_parse_value(raw):
    """Parse a YAML scalar value from its string representation."""
    stripped = raw.strip()
    if stripped == "" or stripped == "~" or stripped.lower() == "null":
        return None
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False
    if stripped.startswith('"') and stripped.endswith('"'):
        return stripped[1:-1].replace('\\"', '"').replace("\\n", "\n")
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1].replace("''", "'")
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        pass
    return stripped


def _count_indent(line):
    return len(line) - len(line.lstrip(" "))


def parse_yaml(text):
    """Parse a simple YAML document into Python dicts/lists/scalars.

    Handles:
      - Mappings (key: value)
      - Sequences (- item)
      - Literal block scalars (|)
      - Folded block scalars (>)
      - Nested structures
      - Quoted strings with special characters
    """
    lines = text.split("\n")
    # Strip trailing empty lines
    while lines and lines[-1].strip() == "":
        lines.pop()
    result, _ = _parse_yaml_node(lines, 0, 0)
    return result


def _parse_yaml_node(lines, start, min_indent):
    """Recursively parse a YAML node starting at line `start`."""
    if start >= len(lines):
        return None, start

    # Skip blank lines and comments
    while start < len(lines):
        stripped = lines[start].strip()
        if stripped == "" or stripped.startswith("#"):
            start += 1
            continue
        break

    if start >= len(lines):
        return None, start

    line = lines[start]
    indent = _count_indent(line)
    stripped = line.strip()

    if indent < min_indent:
        return None, start

    # Sequence item
    if stripped.startswith("- "):
        return _parse_yaml_list(lines, start, indent)

    # Mapping
    if ":" in stripped and not stripped.startswith("{"):
        return _parse_yaml_mapping(lines, start, indent)

    return _yaml_parse_value(stripped), start + 1


def _parse_yaml_list(lines, start, list_indent):
    result = []
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        indent = _count_indent(lines[i])
        if indent < list_indent:
            break
        if indent > list_indent:
            break
        if not stripped.startswith("- "):
            break

        item_text = stripped[2:].strip()

        # Inline mapping after dash: - key: value
        if ":" in item_text and not item_text.startswith('"') and not item_text.startswith("'"):
            colon_pos = item_text.index(":")
            key = item_text[:colon_pos].strip()
            val_text = item_text[colon_pos + 1:].strip()

            if val_text == "" or val_text == "|" or val_text == ">":
                # Block scalar or nested mapping
                mapping = {}
                if val_text == "|" or val_text == ">":
                    block_val, i = _parse_block_scalar(lines, i + 1, indent + 2, val_text == ">")
                    mapping[key] = block_val
                else:
                    mapping[key], i = _parse_yaml_node(lines, i + 1, indent + 2)
                # Continue reading sibling keys at same indent + 2
                while i < len(lines):
                    s = lines[i].strip()
                    if s == "" or s.startswith("#"):
                        i += 1
                        continue
                    ci = _count_indent(lines[i])
                    if ci <= indent:
                        break
                    if ":" in s:
                        k2, v2, i = _parse_yaml_key_value(lines, i, ci)
                        mapping[k2] = v2
                    else:
                        break
                result.append(mapping)
            else:
                mapping = {key: _yaml_parse_value(val_text)}
                i += 1
                # Continue reading sibling keys
                while i < len(lines):
                    s = lines[i].strip()
                    if s == "" or s.startswith("#"):
                        i += 1
                        continue
                    ci = _count_indent(lines[i])
                    if ci <= indent:
                        break
                    if ":" in s:
                        k2, v2, i = _parse_yaml_key_value(lines, i, ci)
                        mapping[k2] = v2
                    else:
                        break
                result.append(mapping)
        else:
            # Simple scalar list item
            result.append(_yaml_parse_value(item_text))
            i += 1

    return result, i


def _parse_yaml_mapping(lines, start, map_indent):
    result = {}
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        indent = _count_indent(lines[i])
        if indent < map_indent:
            break
        if indent > map_indent:
            break
        if ":" not in stripped:
            break

        key, val, i = _parse_yaml_key_value(lines, i, indent)
        result[key] = val

    return result, i


def _parse_yaml_key_value(lines, i, indent):
    """Parse a single key: value pair, handling block scalars and nested nodes."""
    stripped = lines[i].strip()
    colon_idx = stripped.index(":")
    key = stripped[:colon_idx].strip()
    val_text = stripped[colon_idx + 1:].strip()

    if val_text == "|":
        val, next_i = _parse_block_scalar(lines, i + 1, indent + 2, fold=False)
        return key, val, next_i
    elif val_text == ">":
        val, next_i = _parse_block_scalar(lines, i + 1, indent + 2, fold=True)
        return key, val, next_i
    elif val_text == "":
        # Nested structure
        val, next_i = _parse_yaml_node(lines, i + 1, indent + 1)
        return key, val, next_i
    else:
        return key, _yaml_parse_value(val_text), i + 1


def _parse_block_scalar(lines, start, min_indent, fold):
    """Parse a YAML literal (|) or folded (>) block scalar."""
    collected = []
    i = start
    while i < len(lines):
        if lines[i].strip() == "":
            collected.append("")
            i += 1
            continue
        ci = _count_indent(lines[i])
        if ci < min_indent:
            break
        collected.append(lines[i][min_indent:] if len(lines[i]) >= min_indent else lines[i].lstrip())
        i += 1

    # Strip trailing empty lines
    while collected and collected[-1] == "":
        collected.pop()

    if fold:
        return " ".join(collected)
    else:
        return "\n".join(collected)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_json_config():
    """Load the main brand_config.json."""
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml_configs():
    """Discover and load all configs/*.yaml or configs/*.json files, sorted alphabetically.

    JSON files are preferred for complex multi-line find/replace strings
    (identical schema to brand_config.json). YAML files are also supported
    for simple configs.
    """
    if not CONFIGS_DIR.exists():
        return []
    config_files = sorted(
        list(CONFIGS_DIR.glob("*.json")) + list(CONFIGS_DIR.glob("*.yaml")),
        key=lambda p: p.name,
    )
    configs = []
    for cf in config_files:
        text = cf.read_text(encoding="utf-8")
        if cf.suffix == ".json":
            parsed = json.loads(text)
        else:
            parsed = parse_yaml(text)
        if parsed and isinstance(parsed, dict):
            parsed["_source_file"] = cf.name
            configs.append(parsed)
    return configs


def merge_configs(json_cfg, yaml_cfgs):
    """Merge JSON config with YAML configs into unified lists."""
    all_string_replacements = list(json_cfg.get("string_replacements", []))
    all_files_to_backup = list(json_cfg.get("files_to_backup", []))
    icon_composer = json_cfg.get("icon_composer", {})
    icon_files = list(json_cfg.get("icon_files", []))
    all_file_copies = list(json_cfg.get("file_copies", []))

    sources = {}
    for entry in all_string_replacements:
        sources[entry["file"]] = "brand_config.json"

    for ycfg in yaml_cfgs:
        src = ycfg.get("_source_file", "unknown.yaml")
        for entry in ycfg.get("string_replacements", []):
            all_string_replacements.append(entry)
            sources[entry["file"]] = src
        for f in ycfg.get("files_to_backup", []):
            if f not in all_files_to_backup:
                all_files_to_backup.append(f)
        if "icon_composer" in ycfg and not icon_composer:
            icon_composer = ycfg["icon_composer"]
        for entry in ycfg.get("icon_files", []):
            icon_files.append(entry)
        for entry in ycfg.get("file_copies", []):
            all_file_copies.append(entry)
            sources[entry["target"]] = src

    return {
        "string_replacements": all_string_replacements,
        "files_to_backup": all_files_to_backup,
        "icon_composer": icon_composer,
        "icon_files": icon_files,
        "file_copies": all_file_copies,
        "_sources": sources,
    }


# ---------------------------------------------------------------------------
# Replacement engine — supports both single-line and multi-line find/replace
# ---------------------------------------------------------------------------

def apply_replacements_to_text(text, replacements):
    """Apply all find/replace pairs and return (new_text, list_of_changes).

    Works on the full text so multi-line find strings are supported.
    """
    changes = []

    for rep in replacements:
        find_str = rep["find"]
        replace_str = rep["replace"]

        count = text.count(find_str)
        if count == 0:
            continue

        # Find the line number of the first occurrence for reporting
        idx = text.find(find_str)
        if idx >= 0:
            line_num = text[:idx].count("\n") + 1
            # Show first line of find and first line of replace in the diff
            find_first_line = find_str.split("\n")[0].strip()
            replace_first_line = replace_str.split("\n")[0].strip()
            changes.append({
                "find": find_str,
                "replace": replace_str,
                "line_num": line_num,
                "before_line": find_first_line,
                "after_line": replace_first_line,
                "occurrences": count,
            })

        text = text.replace(find_str, replace_str)

    return text, changes


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_file_header(rel_path, source=None):
    source_tag = f"  ({DIM}{source}{RESET}{BOLD}{CYAN})" if source else ""
    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  FILE: {rel_path}{source_tag}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}")


def print_change(change):
    line_num = change["line_num"]
    before = change["before_line"]
    after = change["after_line"]
    occurrences = change.get("occurrences", 1)
    occ_tag = f" ({occurrences}x)" if occurrences > 1 else ""
    find_lines = change["find"].count("\n") + 1
    replace_lines = change["replace"].count("\n") + 1
    size_tag = f" [{find_lines}→{replace_lines} lines]" if find_lines > 1 or replace_lines > 1 else ""
    print(f"\n  {YELLOW}Line {line_num}{occ_tag}{size_tag}:{RESET}")
    print(f"  {RED}- {before.strip()}{RESET}")
    print(f"  {GREEN}+ {after.strip()}{RESET}")


def print_icon_change(source, target, exists):
    status = f"{GREEN}READY{RESET}" if exists else f"{RED}MISSING SOURCE{RESET}"
    print(f"\n  {YELLOW}Icon copy:{RESET}  [{status}]")
    print(f"  {RED}- {target}{RESET}")
    print(f"  {GREEN}+ (replaced with {source}){RESET}")


def find_ictool():
    """Locate the ictool binary inside Xcode's Icon Composer app."""
    try:
        result = subprocess.run(
            ["xcode-select", "-p"], capture_output=True, text=True, check=True
        )
        xcode_dev = Path(result.stdout.strip())
        ictool = (
            xcode_dev.parent
            / "Applications"
            / "Icon Composer.app"
            / "Contents"
            / "Executables"
            / "ictool"
        )
        if ictool.exists():
            return ictool
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def auto_export_preview(icon_source, preview_dest, warnings):
    """Try to generate AppIcon-preview.png from the .icon bundle via ictool."""
    ictool = find_ictool()
    if not ictool:
        warnings.append(
            "ictool not found (requires Xcode 26+). "
            "Export a preview PNG manually: Icon Composer → File → Export → "
            "save as Assets/AppIcon-preview.png"
        )
        return False

    try:
        subprocess.run(
            [
                str(ictool),
                str(icon_source),
                "--export-preview", "iOS", "Light",
                "1024", "1024", "1",
                str(preview_dest),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        warnings.append(
            f"ictool export failed: {e.stderr.strip() or e.stdout.strip() or str(e)}. "
            "Export a preview PNG manually from Icon Composer."
        )
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    mode = "--dry-run"
    if "--apply" in sys.argv:
        mode = "--apply"
    elif "--dry-run" in sys.argv:
        mode = "--dry-run"

    json_config = load_json_config()
    yaml_configs = load_yaml_configs()
    merged = merge_configs(json_config, yaml_configs)

    string_replacements = merged["string_replacements"]
    file_copies = merged["file_copies"]
    icon_composer = merged["icon_composer"]
    icon_files = merged["icon_files"]
    sources = merged["_sources"]

    is_apply = mode == "--apply"
    mode_label = f"{RED}APPLY{RESET}" if is_apply else f"{YELLOW}DRY RUN{RESET}"

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  OVERRIDE — ChatFort Brand  [{mode_label}{BOLD}{CYAN}]{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}")

    # Show loaded config sources
    if yaml_configs:
        print(f"\n  {DIM}Config sources:{RESET}")
        print(f"    {DIM}1. brand_config.json{RESET}")
        for idx, yc in enumerate(yaml_configs, start=2):
            name = yc.get("name", yc.get("_source_file", "?"))
            desc = yc.get("description", "")
            print(f"    {DIM}{idx}. {yc['_source_file']}  ({name}){RESET}")

    total_changes = 0
    total_files = 0
    total_icons = 0
    warnings = []

    # --- String replacements ---
    for file_entry in string_replacements:
        rel_path = file_entry["file"]
        replacements = file_entry["replacements"]
        full_path = REPO_ROOT / rel_path

        if not full_path.exists():
            warnings.append(f"File not found: {rel_path}")
            continue

        try:
            original_text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings.append(f"Cannot read as text: {rel_path}")
            continue

        new_text, changes = apply_replacements_to_text(original_text, replacements)

        if not changes:
            continue

        source = sources.get(rel_path, "")
        print_file_header(rel_path, source)
        for change in changes:
            print_change(change)

        total_changes += len(changes)
        total_files += 1

        if is_apply and new_text != original_text:
            full_path.write_text(new_text, encoding="utf-8")
            print(f"\n  {GREEN}Written {len(changes)} changes.{RESET}")

    # --- File copies (Swift files injected into the project) ---
    for fc_entry in file_copies:
        source_rel = fc_entry["source"]
        target_rel = fc_entry["target"]
        source_path = BRAND_DIR / source_rel
        target_path = REPO_ROOT / target_rel

        if not source_path.exists():
            warnings.append(f"File copy source missing: {source_rel}")
            continue

        source_cfg = sources.get(target_rel, "")
        print_file_header(target_rel, source_cfg)
        already_exists = target_path.exists()
        status = (
            f"{YELLOW}UPDATE{RESET}" if already_exists
            else f"{GREEN}NEW{RESET}"
        )
        print(f"\n  {YELLOW}File copy:{RESET}  [{status}]")
        print(f"  {GREEN}+ {source_rel} → {target_rel}{RESET}")

        total_icons += 1
        if is_apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_path), str(target_path))
            print(f"\n  {GREEN}File copied.{RESET}")

    # --- Icon Composer bundle (.icon) ---
    if icon_composer:
        source_rel = icon_composer["source"]
        source_path = BRAND_DIR / source_rel

        if not source_path.exists():
            warnings.append(
                f"Icon Composer bundle missing: {source_rel} — "
                "create your icon in Icon Composer and save as "
                f"tools/BrandOverride/{source_rel}"
            )
        else:
            for target_rel in icon_composer.get("targets", []):
                target_path = REPO_ROOT / target_rel

                print_file_header(target_rel)
                already_exists = target_path.exists()
                status = (
                    f"{YELLOW}UPDATE{RESET}" if already_exists
                    else f"{GREEN}NEW{RESET}"
                )
                print(f"\n  {YELLOW}Icon Composer bundle:{RESET}  [{status}]")
                print(f"  {GREEN}+ {source_rel} → {target_rel}{RESET}")

                total_icons += 1
                if is_apply:
                    if target_path.exists():
                        shutil.rmtree(str(target_path))
                    shutil.copytree(str(source_path), str(target_path))
                    print(f"\n  {GREEN}Bundle copied.{RESET}")

    # --- Auto-export preview PNG if missing ---
    preview_path = BRAND_DIR / "Assets" / "AppIcon-preview.png"
    icon_source_path = BRAND_DIR / icon_composer.get("source", "")
    if icon_composer and not preview_path.exists() and icon_source_path.exists():
        print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
        print(f"{BOLD}{CYAN}  Auto-exporting preview PNG via ictool...{RESET}")
        print(f"{BOLD}{CYAN}{'━' * 60}{RESET}")
        if is_apply:
            if auto_export_preview(icon_source_path, preview_path, warnings):
                print(f"  {GREEN}Exported AppIcon-preview.png{RESET}")
        else:
            ictool = find_ictool()
            if ictool:
                print(f"  {YELLOW}Will export AppIcon-preview.png via ictool{RESET}")
            else:
                warnings.append(
                    "AppIcon-preview.png not found and ictool not available. "
                    "Export manually: Icon Composer → File → Export → "
                    "save as Assets/AppIcon-preview.png"
                )

    # --- Icon preview files (PNG for in-app display) ---
    for icon_entry in icon_files:
        source_rel = icon_entry["source"]
        target_rel = icon_entry["target"]
        source_path = BRAND_DIR / source_rel
        target_path = REPO_ROOT / target_rel

        source_exists = source_path.exists()

        if not target_path.exists() and not source_exists:
            warnings.append(
                f"Icon source missing: {source_rel} — "
                f"export from Icon Composer and place at "
                f"tools/BrandOverride/{source_rel}"
            )
            continue

        if target_path.exists():
            print_file_header(target_rel)
            print_icon_change(source_rel, target_rel, source_exists)

        if source_exists:
            total_icons += 1
            if is_apply:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(source_path), str(target_path))
                print(f"\n  {GREEN}Icon replaced.{RESET}")
        elif not target_path.exists():
            pass
        else:
            warnings.append(
                f"Icon source missing: {source_rel} — "
                f"export from Icon Composer and place at "
                f"tools/BrandOverride/{source_rel}"
            )

    # --- Summary ---
    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    config_count = 1 + len(yaml_configs)
    config_note = f" from {config_count} config{'s' if config_count > 1 else ''}" if yaml_configs else ""
    if is_apply:
        print(f"  {GREEN}APPLIED: {total_changes} string changes across {total_files} files{config_note}{RESET}")
        if total_icons:
            print(f"  {GREEN}APPLIED: {total_icons} icon operations{RESET}")
    else:
        print(f"  {YELLOW}DRY RUN: {total_changes} string changes across {total_files} files{config_note}{RESET}")
        if total_icons:
            print(f"  {YELLOW}DRY RUN: {total_icons} icon operations ready{RESET}")
        print(f"\n  {DIM}Run with --apply to write changes to disk.{RESET}")

    if warnings:
        print(f"\n  {RED}WARNINGS:{RESET}")
        for w in warnings:
            print(f"    {YELLOW}⚠  {w}{RESET}")

    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
