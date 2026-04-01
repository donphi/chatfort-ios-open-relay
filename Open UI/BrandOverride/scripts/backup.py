#!/usr/bin/env python3
"""
backup.py — Snapshot all brandable upstream files into a versioned backup folder.

Creates two subdirectories inside backups/:
  - pristine/  : exact copies of upstream files, NEVER edited (used by restore.py)
  - override/  : identical copies kept as reference

Usage:
    python3 backup.py                   # auto-detect version
    python3 backup.py --tag my-label    # append custom label to folder name
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRAND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BRAND_DIR.parent.parent  # Open UI/BrandOverride -> Open UI -> repo root
CONFIG_PATH = BRAND_DIR / "brand_config.json"
BACKUPS_DIR = BRAND_DIR / "backups"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_marketing_version():
    pbxproj = REPO_ROOT / "Open UI.xcodeproj" / "project.pbxproj"
    if not pbxproj.exists():
        return "unknown", "0"
    text = pbxproj.read_text(encoding="utf-8")
    ver_match = re.search(r'MARKETING_VERSION\s*=\s*([^;]+);', text)
    build_match = re.search(r'CURRENT_PROJECT_VERSION\s*=\s*([^;]+);', text)
    version = ver_match.group(1).strip() if ver_match else "unknown"
    build = build_match.group(1).strip() if build_match else "0"
    return version, build


def get_git_hash():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip() if result.returncode == 0 else "nohash"
    except FileNotFoundError:
        return "nohash"


def main():
    custom_tag = None
    if "--tag" in sys.argv:
        idx = sys.argv.index("--tag")
        if idx + 1 < len(sys.argv):
            custom_tag = sys.argv[idx + 1]

    config = load_config()
    files_to_backup = config["files_to_backup"]

    version, build = get_marketing_version()
    git_hash = get_git_hash()
    date_str = datetime.now().strftime("%Y-%m-%d")

    folder_name = f"v{version}_build{build}_{date_str}_{git_hash}"
    if custom_tag:
        folder_name += f"_{custom_tag}"

    backup_root = BACKUPS_DIR / folder_name
    pristine_dir = backup_root / "pristine"
    override_dir = backup_root / "override"

    if backup_root.exists():
        print(f"{YELLOW}Backup folder already exists: {folder_name}{RESET}")
        print(f"{YELLOW}Overwriting...{RESET}")
        shutil.rmtree(backup_root)

    pristine_dir.mkdir(parents=True, exist_ok=True)
    override_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  BACKUP: {folder_name}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    backed_up = 0
    missing = 0

    for rel_path in files_to_backup:
        src = REPO_ROOT / rel_path
        if not src.exists():
            print(f"  {RED}MISSING{RESET}  {rel_path}")
            missing += 1
            continue

        for dest_dir in (pristine_dir, override_dir):
            dest = dest_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dest))

        size = src.stat().st_size
        size_str = f"{size:,} bytes" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
        print(f"  {GREEN}OK{RESET}  {rel_path}  ({size_str})")
        backed_up += 1

    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"  {GREEN}{backed_up} files backed up{RESET}", end="")
    if missing:
        print(f"  |  {RED}{missing} files missing{RESET}", end="")
    print(f"\n  Location: {backup_root.relative_to(BRAND_DIR)}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")

    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
