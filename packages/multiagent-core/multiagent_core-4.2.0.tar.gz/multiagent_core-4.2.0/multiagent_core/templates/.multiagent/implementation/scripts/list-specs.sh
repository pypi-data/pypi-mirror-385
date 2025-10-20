#!/bin/bash
set -euo pipefail

# List all available specs
# Usage: list-specs.sh
# Output: One spec per line in format "ID: name"

ls -d specs/[0-9][0-9][0-9]-* 2>/dev/null | while read spec; do
  SPEC_NAME=$(basename "$spec")
  SPEC_ID=$(echo "$SPEC_NAME" | cut -d'-' -f1)
  SPEC_TITLE=$(echo "$SPEC_NAME" | cut -d'-' -f2-)
  echo "$SPEC_ID: $SPEC_TITLE"
done
