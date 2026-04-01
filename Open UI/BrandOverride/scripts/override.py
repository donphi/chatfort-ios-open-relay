#!/usr/bin/env python3
"""
override.py — Apply ChatFort brand changes to upstream files.

Reads brand_config.json for all string replacements and icon file copies,
then either previews (--dry-run) or applies (--apply) the changes.

Usage:
    python3 override.py              # default: --dry-run
    python3 override.py --dry-run    # show colored diff, write nothing
    python3 override.py --apply      # show colored diff, then write changes
"""

import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRAND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BRAND_DIR.parent.parent
CONFIG_PATH = BRAND_DIR / "brand_config.json"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_replacement_positions(original_lines, find_str):
    """Return list of (line_index, col_start) for every occurrence of find_str."""
    positions = []
    for i, line in enumerate(original_lines):
        col = 0
        while True:
            idx = line.find(find_str, col)
            if idx == -1:
                break
            positions.append((i, idx))
            col = idx + len(find_str)
    return positions


def apply_replacements_to_text(text, replacements):
    """Apply all find/replace pairs and return (new_text, list_of_changes).

    Each change is a dict with keys: find, replace, line_num, before_line, after_line.
    """
    changes = []
    lines = text.splitlines(keepends=True)

    for rep in replacements:
        find_str = rep["find"]
        replace_str = rep["replace"]

        positions = find_replacement_positions(
            [l.rstrip('\n').rstrip('\r') for l in lines], find_str
        )

        for line_idx, _ in positions:
            before_line = lines[line_idx].rstrip('\n').rstrip('\r')
            after_line = before_line.replace(find_str, replace_str)
            changes.append({
                "find": find_str,
                "replace": replace_str,
                "line_num": line_idx + 1,
                "before_line": before_line,
                "after_line": after_line,
            })

        new_lines = []
        for line in lines:
            new_lines.append(line.replace(find_str, replace_str))
        lines = new_lines

    result = "".join(lines)
    return result, changes


def print_file_header(rel_path):
    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  FILE: {rel_path}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}")


def print_change(change):
    line_num = change["line_num"]
    before = change["before_line"]
    after = change["after_line"]
    print(f"\n  {YELLOW}Line {line_num}:{RESET}")
    print(f"  {RED}- {before.strip()}{RESET}")
    print(f"  {GREEN}+ {after.strip()}{RESET}")


def print_icon_change(source, target, exists):
    status = f"{GREEN}READY{RESET}" if exists else f"{RED}MISSING SOURCE{RESET}"
    print(f"\n  {YELLOW}Icon copy:{RESET}  [{status}]")
    print(f"  {RED}- {target}{RESET}")
    print(f"  {GREEN}+ (replaced with {source}){RESET}")


def main():
    mode = "--dry-run"
    if "--apply" in sys.argv:
        mode = "--apply"
    elif "--dry-run" in sys.argv:
        mode = "--dry-run"

    config = load_config()
    string_replacements = config.get("string_replacements", [])
    icon_files = config.get("icon_files", [])

    is_apply = mode == "--apply"
    mode_label = f"{RED}APPLY{RESET}" if is_apply else f"{YELLOW}DRY RUN{RESET}"

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  OVERRIDE — ChatFort Brand  [{mode_label}{BOLD}{CYAN}]{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}")

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

        print_file_header(rel_path)
        for change in changes:
            print_change(change)

        total_changes += len(changes)
        total_files += 1

        if is_apply and new_text != original_text:
            full_path.write_text(new_text, encoding="utf-8")
            print(f"\n  {GREEN}Written {len(changes)} changes.{RESET}")

    # --- Icon files ---
    for icon_entry in icon_files:
        source_rel = icon_entry["source"]
        target_rel = icon_entry["target"]
        source_path = BRAND_DIR / source_rel
        target_path = REPO_ROOT / target_rel

        source_exists = source_path.exists()

        if not target_path.exists() and not source_exists:
            warnings.append(f"Icon source missing: {source_rel} — place your ChatFort icon at BrandOverride/{source_rel}")
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
            pass  # warning already added
        else:
            warnings.append(
                f"Icon source missing: {source_rel} — place your ChatFort icon at "
                f"BrandOverride/{source_rel}"
            )

    # --- Icon Contents.json updates (dark/tinted variants) ---
    icon_contents = config.get("icon_contents_json", [])
    for entry in icon_contents:
        target_dir = REPO_ROOT / entry["target_dir"]
        contents_path = target_dir / "Contents.json"

        if not contents_path.exists():
            warnings.append(f"Contents.json not found: {entry['target_dir']}")
            continue

        dark_source = BRAND_DIR / "Assets" / "AppIcon-dark.png"
        tinted_source = BRAND_DIR / "Assets" / "AppIcon-tinted.png"
        has_dark = dark_source.exists()
        has_tinted = tinted_source.exists()

        if not has_dark and not has_tinted:
            continue

        contents_data = json.loads(contents_path.read_text(encoding="utf-8"))
        changed = False

        for image in contents_data.get("images", []):
            appearances = image.get("appearances", [])
            if not appearances:
                continue
            for app in appearances:
                if app.get("appearance") == "luminosity":
                    if app.get("value") == "dark" and has_dark:
                        if image.get("filename") != entry["dark_filename"]:
                            print_file_header(f"{entry['target_dir']}/Contents.json")
                            old_val = image.get("filename", "(empty)")
                            print(f"\n  {YELLOW}Dark icon slot:{RESET}")
                            print(f"  {RED}- filename: {old_val}{RESET}")
                            print(f"  {GREEN}+ filename: {entry['dark_filename']}{RESET}")
                            image["filename"] = entry["dark_filename"]
                            changed = True
                    elif app.get("value") == "tinted" and has_tinted:
                        if image.get("filename") != entry["tinted_filename"]:
                            if not changed:
                                print_file_header(f"{entry['target_dir']}/Contents.json")
                            old_val = image.get("filename", "(empty)")
                            print(f"\n  {YELLOW}Tinted icon slot:{RESET}")
                            print(f"  {RED}- filename: {old_val}{RESET}")
                            print(f"  {GREEN}+ filename: {entry['tinted_filename']}{RESET}")
                            image["filename"] = entry["tinted_filename"]
                            changed = True

        if changed:
            total_files += 1
            if is_apply:
                new_json = json.dumps(contents_data, indent=2, ensure_ascii=False) + "\n"
                contents_path.write_text(new_json, encoding="utf-8")
                print(f"\n  {GREEN}Contents.json updated.{RESET}")

    # --- Summary ---
    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    if is_apply:
        print(f"  {GREEN}APPLIED: {total_changes} string changes across {total_files} files{RESET}")
        if total_icons:
            print(f"  {GREEN}APPLIED: {total_icons} icon replacements{RESET}")
    else:
        print(f"  {YELLOW}DRY RUN: {total_changes} string changes across {total_files} files{RESET}")
        if total_icons:
            print(f"  {YELLOW}DRY RUN: {total_icons} icon replacements ready{RESET}")
        print(f"\n  {DIM}Run with --apply to write changes to disk.{RESET}")

    if warnings:
        print(f"\n  {RED}WARNINGS:{RESET}")
        for w in warnings:
            print(f"    {YELLOW}⚠  {w}{RESET}")

    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
