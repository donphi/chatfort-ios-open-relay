#!/usr/bin/env bash
# Wrapper for backup.py — run from anywhere.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/backup.py" "$@"
