#!/bin/bash
set -euo pipefail

# Create new spec directory structure
# Usage: create-spec-directory.sh --spec-id 008 --name redis-caching
# Output: Creates directory and placeholder spec.md

SPEC_ID=""
NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spec-id)
      SPEC_ID="$2"
      shift 2
      ;;
    --name)
      NAME="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Validate inputs
if [[ -z "$SPEC_ID" ]] || [[ -z "$NAME" ]]; then
  echo "Usage: create-spec-directory.sh --spec-id 008 --name redis-caching" >&2
  exit 1
fi

# Create directory
SPEC_DIR="specs/${SPEC_ID}-${NAME}"
mkdir -p "$SPEC_DIR"

# Create placeholder spec.md
cat > "$SPEC_DIR/spec.md" << EOF
# Spec: $NAME

**ID**: $SPEC_ID
**Created**: $(date +%Y-%m-%d)

## Overview

[To be filled after implementation planning]

## Status

- Phase: Planning
- Created: $(date +%Y-%m-%d)
EOF

echo "$SPEC_DIR"
