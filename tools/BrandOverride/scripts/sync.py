#!/usr/bin/env python3
"""
sync.py — Safely sync the fork with upstream, preserving fork-only files.

This script replaces the manual workflow of:
    restore.sh → git pull upstream main → backup.sh

It performs these steps atomically:
    1. Fetch latest upstream/main
    2. Run restore (undo brand overrides)
    3. Stash fork-only paths to a temp directory
    4. git reset --hard upstream/main
    5. Restore fork-only paths from the stash
    6. Run backup (snapshot the new upstream state)
    7. Summary

Usage:
    python3 sync.py              # fetch + reset + backup
    python3 sync.py --dry-run    # show what would happen without changing anything
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
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

DIVIDER = f"{BOLD}{CYAN}{'━' * 60}{RESET}"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_git(*args, check=True, capture=True):
    cmd = ["git", "-C", str(REPO_ROOT)] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result


def get_current_branch():
    r = run_git("rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip()


def get_commit_short(ref):
    r = run_git("rev-parse", "--short", ref, check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def get_commit_subject(ref):
    r = run_git("log", "-1", "--format=%s", ref, check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def has_uncommitted_changes():
    r = run_git("status", "--porcelain")
    return bool(r.stdout.strip())


def main():
    dry_run = "--dry-run" in sys.argv

    config = load_config()
    fork_only_paths = config.get("fork_only_paths", [])

    if not fork_only_paths:
        print(f"{RED}No fork_only_paths defined in brand_config.json{RESET}")
        return 1

    mode_label = f"[{YELLOW}DRY RUN{RESET}{BOLD}{CYAN}]" if dry_run else ""
    print(f"\n{DIVIDER}")
    print(f"{BOLD}{CYAN}  SYNC — Upstream → Fork  {mode_label}{RESET}")
    print(DIVIDER)

    # --- Pre-flight checks ---
    branch = get_current_branch()
    if branch != "main":
        print(f"\n  {RED}ERROR: Not on main branch (currently on '{branch}'){RESET}")
        print(f"  {DIM}Switch to main first: git checkout main{RESET}")
        return 1

    if has_uncommitted_changes():
        print(f"\n  {RED}ERROR: Uncommitted changes detected{RESET}")
        print(f"  {DIM}Commit or stash your changes first.{RESET}")
        return 1

    local_sha = get_commit_short("HEAD")
    local_subject = get_commit_subject("HEAD")
    print(f"\n  {DIM}Local HEAD:{RESET}  {local_sha} {local_subject}")

    # --- Step 1: Fetch upstream ---
    print(f"\n  {CYAN}[1/6]{RESET} Fetching upstream...")
    if not dry_run:
        r = run_git("fetch", "upstream", "main", check=False)
        if r.returncode != 0:
            print(f"  {RED}ERROR: Could not fetch upstream/main{RESET}")
            print(f"  {DIM}Make sure 'upstream' remote is configured:{RESET}")
            print(f"  {DIM}  git remote add upstream https://github.com/Ichigo3766/Open-Relay.git{RESET}")
            return 1

    upstream_sha = get_commit_short("upstream/main")
    upstream_subject = get_commit_subject("upstream/main")
    if not upstream_sha:
        print(f"  {RED}ERROR: upstream/main not found{RESET}")
        return 1
    print(f"  {DIM}Upstream HEAD:{RESET} {upstream_sha} {upstream_subject}")

    if local_sha == upstream_sha:
        print(f"\n  {GREEN}Already up to date with upstream.{RESET}")
        print(DIVIDER)
        return 0

    # --- Step 2: Run restore (undo overrides) ---
    print(f"\n  {CYAN}[2/6]{RESET} Restoring upstream file contents (undoing overrides)...")
    if not dry_run:
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "restore.py")],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print(f"  {YELLOW}WARNING: restore.py returned non-zero (may be first run){RESET}")

    # --- Step 3: Stash fork-only paths ---
    print(f"\n  {CYAN}[3/6]{RESET} Protecting fork-only paths...")
    stash_dir = Path(tempfile.mkdtemp(prefix="brandoverride_sync_"))
    stashed = []

    for rel_path in fork_only_paths:
        src = REPO_ROOT / rel_path
        dst = stash_dir / rel_path
        if src.exists():
            print(f"         {GREEN}STASH{RESET}  {rel_path}")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    shutil.copytree(str(src), str(dst))
                else:
                    shutil.copy2(str(src), str(dst))
            stashed.append(rel_path)
        else:
            print(f"         {DIM}SKIP{RESET}   {rel_path}  (not present)")

    if not stashed:
        print(f"  {RED}ERROR: No fork-only paths found to protect. Aborting.{RESET}")
        shutil.rmtree(str(stash_dir), ignore_errors=True)
        return 1

    # --- Step 4: Hard reset to upstream ---
    print(f"\n  {CYAN}[4/6]{RESET} Resetting to upstream/main ({upstream_sha})...")
    if not dry_run:
        run_git("reset", "--hard", "upstream/main")

    # --- Step 5: Restore fork-only paths ---
    print(f"\n  {CYAN}[5/6]{RESET} Restoring fork-only paths...")
    restored = 0
    for rel_path in stashed:
        src = stash_dir / rel_path
        dst = REPO_ROOT / rel_path
        print(f"         {GREEN}RESTORE{RESET}  {rel_path}")
        if not dry_run:
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(str(dst))
                else:
                    dst.unlink()
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(str(src), str(dst))
            else:
                shutil.copy2(str(src), str(dst))
        restored += 1

    shutil.rmtree(str(stash_dir), ignore_errors=True)

    # --- Step 6: Run backup ---
    print(f"\n  {CYAN}[6/6]{RESET} Creating backup of new upstream state...")
    if not dry_run:
        r = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "backup.py")],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            for line in r.stdout.strip().splitlines():
                if "BACKUP" in line or "files backed up" in line or "━" in line:
                    print(f"         {line}")
        else:
            print(f"  {YELLOW}WARNING: backup.py returned non-zero{RESET}")
            if r.stderr:
                print(f"  {DIM}{r.stderr.strip()}{RESET}")

    # --- Summary ---
    print(f"\n{DIVIDER}")
    if dry_run:
        print(f"  {YELLOW}DRY RUN complete — no changes made{RESET}")
        print(f"  Would reset: {local_sha} → {upstream_sha}")
        print(f"  Would protect: {len(stashed)} fork-only paths")
    else:
        new_sha = get_commit_short("HEAD")
        print(f"  {GREEN}Sync complete:{RESET} {local_sha} → {new_sha} ({upstream_subject})")
        print(f"  {GREEN}{restored} fork-only paths preserved{RESET}")
        print(f"\n  {DIM}Next steps:{RESET}")
        print(f"    1. ./scripts/override.sh --dry-run   {DIM}# preview changes{RESET}")
        print(f"    2. ./scripts/override.sh --apply     {DIM}# apply ChatFort branding{RESET}")
        print(f"    3. git add -A && git commit           {DIM}# commit everything{RESET}")
        print(f"    4. git push --force-with-lease        {DIM}# update your fork{RESET}")
    print(DIVIDER)

    return 0


if __name__ == "__main__":
    sys.exit(main())
