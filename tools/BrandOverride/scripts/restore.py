#!/usr/bin/env python3
"""
restore.py — Restore upstream files from a pristine backup.

Copies every file from the pristine/ subdirectory of a backup back to its
original location in the repo, reverting any brand overrides.

Usage:
    python3 restore.py                       # use latest backup
    python3 restore.py --version v2.4_...    # use a specific backup folder name
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
BACKUPS_DIR = BRAND_DIR / "backups"

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


def find_latest_backup():
    if not BACKUPS_DIR.exists():
        return None
    candidates = sorted(
        [d for d in BACKUPS_DIR.iterdir() if d.is_dir() and d.name != ".gitkeep"],
        key=lambda d: d.stat().st_mtime,
        reverse=True
    )
    return candidates[0] if candidates else None


def files_differ(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return True
    return a.read_bytes() != b.read_bytes()


def show_text_diff(pristine_file: Path, current_file: Path, rel_path: str):
    """Show a simple summary of differences for text files."""
    try:
        pristine_lines = pristine_file.read_text(encoding="utf-8").splitlines()
        current_lines = current_file.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        print(f"    {DIM}(binary file — will be replaced){RESET}")
        return

    import difflib
    diff = list(difflib.unified_diff(
        current_lines, pristine_lines,
        fromfile=f"current/{rel_path}",
        tofile=f"pristine/{rel_path}",
        lineterm=""
    ))
    if not diff:
        return

    shown = 0
    for line in diff:
        if shown > 30:
            remaining = len(diff) - shown
            print(f"    {DIM}... and {remaining} more diff lines{RESET}")
            break
        if line.startswith("---") or line.startswith("+++"):
            continue
        elif line.startswith("@@"):
            print(f"    {CYAN}{line}{RESET}")
        elif line.startswith("-"):
            print(f"    {RED}{line}{RESET}")
        elif line.startswith("+"):
            print(f"    {GREEN}{line}{RESET}")
        shown += 1


def main():
    specific_version = None
    if "--version" in sys.argv:
        idx = sys.argv.index("--version")
        if idx + 1 < len(sys.argv):
            specific_version = sys.argv[idx + 1]

    if specific_version:
        backup_root = BACKUPS_DIR / specific_version
        if not backup_root.exists():
            print(f"{RED}Backup not found: {specific_version}{RESET}")
            print(f"Available backups:")
            for d in sorted(BACKUPS_DIR.iterdir()):
                if d.is_dir() and d.name != ".gitkeep":
                    print(f"  {d.name}")
            return 1
    else:
        backup_root = find_latest_backup()
        if not backup_root:
            print(f"{RED}No backups found in {BACKUPS_DIR.relative_to(BRAND_DIR)}{RESET}")
            print(f"Run backup.sh first to create a backup.")
            return 1

    pristine_dir = backup_root / "pristine"
    if not pristine_dir.exists():
        print(f"{RED}No pristine/ directory in {backup_root.name}{RESET}")
        return 1

    config = load_config()
    files_to_restore = config["files_to_backup"]

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  RESTORE from: {backup_root.name}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    restored = 0
    skipped = 0
    missing = 0

    for rel_path in files_to_restore:
        pristine_file = pristine_dir / rel_path
        target_file = REPO_ROOT / rel_path

        if not pristine_file.exists():
            print(f"  {RED}MISSING IN BACKUP{RESET}  {rel_path}")
            missing += 1
            continue

        if target_file.exists() and not files_differ(pristine_file, target_file):
            print(f"  {DIM}UNCHANGED{RESET}  {rel_path}")
            skipped += 1
            continue

        print(f"  {GREEN}RESTORING{RESET}  {rel_path}")
        if target_file.exists():
            show_text_diff(pristine_file, target_file, rel_path)

        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(pristine_file), str(target_file))
        restored += 1

    # Clean up Icon Composer bundles that the override script copied
    # (these don't exist in upstream, so they must be removed on restore)
    cleanup_dirs = [
        "Open UI/AppIcon.icon",
        "OpenUIWidgets/AppIcon.icon",
    ]
    cleaned = 0
    for rel_path in cleanup_dirs:
        target_dir = REPO_ROOT / rel_path
        if target_dir.exists():
            shutil.rmtree(str(target_dir))
            print(f"  {YELLOW}CLEANED{RESET}  {rel_path}/  (not in upstream)")
            cleaned += 1

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"  {GREEN}{restored} files restored{RESET}", end="")
    if skipped:
        print(f"  |  {DIM}{skipped} already matching{RESET}", end="")
    if missing:
        print(f"  |  {RED}{missing} missing from backup{RESET}", end="")
    if cleaned:
        print(f"  |  {YELLOW}{cleaned} override-only files removed{RESET}", end="")
    print(f"\n  Repo is now at upstream state from: {backup_root.name}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
