#!/usr/bin/env bash
# Wrapper for restore.py — run from anywhere.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/restore.py" "$@"
