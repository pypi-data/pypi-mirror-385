#!/usr/bin/env bash
# Script: get-next-id.sh
# Purpose: Calculate next available enhancement ID
# Subsystem: enhancement
# Called by: /enhancement:create slash command
# Outputs: Next enhancement ID (e.g., "001", "042")

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

# Find all enhancement directories
if [[ ! -d "enhancements" ]]; then
    # First enhancement
    echo "001"
    exit 0
fi

# Extract IDs from directory names (format: enhancements/001-slug/)
HIGHEST_ID=$(find enhancements/ -maxdepth 1 -mindepth 1 -type d -name '[0-9][0-9][0-9]-*' 2>/dev/null | \
             sed 's|enhancements/||' | \
             grep -oP '^\d{3}' | \
             sort -n | \
             tail -1)

# Calculate next ID
if [[ -z "$HIGHEST_ID" ]]; then
    NEXT_ID="001"
else
    NEXT_ID=$(printf "%03d" $((10#$HIGHEST_ID + 1)))
fi

echo "$NEXT_ID"
exit 0
