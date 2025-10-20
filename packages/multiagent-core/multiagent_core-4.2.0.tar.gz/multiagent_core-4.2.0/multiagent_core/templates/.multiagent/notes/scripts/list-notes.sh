#!/usr/bin/env bash
# Script: list-notes.sh
# Purpose: Query notes.md with filters (type, priority, status, file)
# Subsystem: notes
# Called by: note-tracker agent, /note:list command
# Outputs: Filtered list of notes to stdout

set -euo pipefail

# --- Configuration ---
NOTES_FILE="${1:-notes.md}"
FILTER_TYPE="${2:-}"        # bug, todo, observation, question, idea, refactor, note
FILTER_PRIORITY="${3:-}"    # p1, p2, p3
FILTER_STATUS="${4:-open}"  # open, closed, all
FILTER_FILE="${5:-}"        # file path

# --- Validation ---
if [ ! -f "$NOTES_FILE" ]; then
  echo "❌ Error: notes.md not found at $NOTES_FILE"
  exit 1
fi

# --- Main Logic ---
echo "[INFO] Filtering notes from $NOTES_FILE..."

# Use grep to filter notes based on criteria
# Note format: ### #ID - [TYPE] [PRIORITY] Title

TEMP_OUTPUT="/tmp/filtered-notes.txt"
> "$TEMP_OUTPUT"

# Step 1: Extract all note sections (from ### to ---)
awk '/^### #[0-9]+/{flag=1} /^---$/{if(flag) print ""; flag=0} flag' "$NOTES_FILE" > /tmp/all-notes.txt

# Step 2: Filter by status (open/closed/all)
if [ "$FILTER_STATUS" = "open" ]; then
  grep -F -A 10 "**Status:** open" /tmp/all-notes.txt > /tmp/status-filtered.txt || true
elif [ "$FILTER_STATUS" = "closed" ]; then
  grep -F -A 10 "**Status:** closed" /tmp/all-notes.txt > /tmp/status-filtered.txt || true
else
  # all - no status filter
  cp /tmp/all-notes.txt /tmp/status-filtered.txt
fi

# Step 3: Filter by type (if provided)
if [ -n "$FILTER_TYPE" ]; then
  TYPE_UPPER=$(echo "$FILTER_TYPE" | tr '[:lower:]' '[:upper:]')
  grep -i "\\[$TYPE_UPPER\\]" /tmp/status-filtered.txt > /tmp/type-filtered.txt || true
else
  cp /tmp/status-filtered.txt /tmp/type-filtered.txt
fi

# Step 4: Filter by priority (if provided)
if [ -n "$FILTER_PRIORITY" ]; then
  PRIORITY_UPPER=$(echo "$FILTER_PRIORITY" | tr '[:lower:]' '[:upper:]')
  grep "\\[$PRIORITY_UPPER\\]" /tmp/type-filtered.txt > /tmp/priority-filtered.txt || true
else
  cp /tmp/type-filtered.txt /tmp/priority-filtered.txt
fi

# Step 5: Filter by file (if provided)
if [ -n "$FILTER_FILE" ]; then
  grep -F "**File:** $FILTER_FILE" /tmp/priority-filtered.txt -A 10 > /tmp/file-filtered.txt || true
else
  cp /tmp/priority-filtered.txt /tmp/file-filtered.txt
fi

# Step 6: Output results
cat /tmp/file-filtered.txt

# Count results
RESULT_COUNT=$(grep -c "^### #" /tmp/file-filtered.txt || echo 0)

echo "" >&2
echo "[INFO] Found $RESULT_COUNT matching notes" >&2

# Cleanup temp files
rm -f /tmp/all-notes.txt /tmp/status-filtered.txt /tmp/type-filtered.txt \
      /tmp/priority-filtered.txt /tmp/file-filtered.txt

exit 0
