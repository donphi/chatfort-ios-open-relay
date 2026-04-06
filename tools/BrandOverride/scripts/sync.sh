#!/usr/bin/env bash
# Wrapper for sync.py — run from anywhere.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/sync.py" "$@"
