#!/usr/bin/env bash
# Script: detect-docs-sprawl.sh
# Purpose: Detect duplicate or misplaced documentation files
# Subsystem: documentation
# Called by: post-commit hook
# Outputs: Queue file with sprawl locations

set -euo pipefail

# --- Configuration ---
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
QUEUE_FILE="$HOME/.multiagent/documentation/.doc-sprawl-queue"

# --- Main Logic ---
echo "[DOC-SPRAWL] Checking for documentation sprawl..."

# Check for docs in wrong locations (outside docs/, specs/, .git/)
WRONG_LOCATIONS=$(find "$PROJECT_ROOT" -name "*.md" \
  -not -path "*/docs/*" \
  -not -path "*/.git/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/specs/*" \
  -not -path "*/.multiagent/*" \
  -not -path "*/build/*" \
  -not -path "*/dist/*" \
  2>/dev/null | grep -E "(README|CONTRIBUTING|ARCHITECTURE)" || true)

if [ -n "$WRONG_LOCATIONS" ]; then
  echo "[DOC-SPRAWL] ⚠️ Found documentation files outside docs/:"
  echo "$WRONG_LOCATIONS"

  # Create queue file
  mkdir -p "$(dirname "$QUEUE_FILE")"
  echo "$(date +%s)|sprawl|$WRONG_LOCATIONS" >> "$QUEUE_FILE"

  echo "[DOC-SPRAWL] Added to queue: $QUEUE_FILE"
else
  echo "[DOC-SPRAWL] ✅ No sprawl detected"
fi

exit 0
