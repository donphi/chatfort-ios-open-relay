#!/usr/bin/env python3
"""
override.py — Apply ChatFort brand changes to upstream files.

Reads brand_config.json for all string replacements, Icon Composer bundle
copies, and preview icon file copies, then either previews (--dry-run) or
applies (--apply) the changes.

Usage:
    python3 override.py              # default: --dry-run
    python3 override.py --dry-run    # show colored diff, write nothing
    python3 override.py --apply      # show colored diff, then write changes
"""

import json
import os
import shutil
import subprocess
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


def main():
    mode = "--dry-run"
    if "--apply" in sys.argv:
        mode = "--apply"
    elif "--dry-run" in sys.argv:
        mode = "--dry-run"

    config = load_config()
    string_replacements = config.get("string_replacements", [])
    icon_composer = config.get("icon_composer", {})
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
    if is_apply:
        print(f"  {GREEN}APPLIED: {total_changes} string changes across {total_files} files{RESET}")
        if total_icons:
            print(f"  {GREEN}APPLIED: {total_icons} icon operations{RESET}")
    else:
        print(f"  {YELLOW}DRY RUN: {total_changes} string changes across {total_files} files{RESET}")
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
