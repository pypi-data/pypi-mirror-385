#!/bin/bash
set -euo pipefail

# Determine next available spec ID
# Usage: next-spec-id.sh
# Output: Next spec ID (e.g., "008")

# Find last spec directory
LAST_SPEC=$(ls -d specs/[0-9][0-9][0-9]-* 2>/dev/null | tail -1)

if [[ -z "$LAST_SPEC" ]]; then
  # No specs exist yet
  echo "001"
else
  # Extract ID and increment
  LAST_ID=$(basename "$LAST_SPEC" | cut -d'-' -f1)
  NEXT_ID=$((10#$LAST_ID + 1))
  printf "%03d" "$NEXT_ID"
fi
