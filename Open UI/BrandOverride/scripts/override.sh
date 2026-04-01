#!/usr/bin/env bash
# Wrapper for override.py — run from anywhere.
# Usage: ./override.sh              (defaults to --dry-run)
#        ./override.sh --dry-run    (preview changes)
#        ./override.sh --apply      (write changes)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/override.py" "$@"
