#!/usr/bin/env bash
# Script: validate-note.sh
# Purpose: Validate that notes.md structure and entries are correct
# Subsystem: notes
# Called by: note-tracker agent, /note:validate command
# Outputs: Validation report to stdout, exit code 0 (valid) or 1 (invalid)

set -euo pipefail

# --- Configuration ---
NOTES_FILE="${1:-notes.md}"

# --- Validation ---
if [ ! -f "$NOTES_FILE" ]; then
  echo "❌ Error: notes.md not found at $NOTES_FILE"
  exit 1
fi

echo "[INFO] Validating notes.md structure and entries..."

ERRORS=0
WARNINGS=0

# --- Validation Checks ---

# Check 1: File has required headers
if ! grep -q "^# Development Notes" "$NOTES_FILE"; then
  echo "❌ Missing main header '# Development Notes'"
  ((ERRORS++))
fi

if ! grep -q "^## Open Notes" "$NOTES_FILE"; then
  echo "❌ Missing '## Open Notes' section"
  ((ERRORS++))
fi

if ! grep -q "^## Closed Notes" "$NOTES_FILE"; then
  echo "⚠️  Missing '## Closed Notes' section (will be created when first note is closed)"
  ((WARNINGS++))
fi

# Check 2: Verify note entry format
# Each note should have: ID, Type, Priority, Created, Status, Description
NOTES_COUNT=$(grep -c "^### #" "$NOTES_FILE" || echo 0)
echo "[INFO] Found $NOTES_COUNT note entries"

# Extract all note IDs
grep "^### #" "$NOTES_FILE" | sed 's/### #\([0-9]*\) -.*/\1/' > /tmp/note-ids.txt

# Check 3: Verify no duplicate IDs
UNIQUE_IDS=$(sort -u /tmp/note-ids.txt | wc -l)
if [ "$NOTES_COUNT" -ne "$UNIQUE_IDS" ]; then
  echo "❌ Duplicate note IDs found!"
  echo "   Total notes: $NOTES_COUNT"
  echo "   Unique IDs: $UNIQUE_IDS"
  ((ERRORS++))

  # Show duplicates
  sort /tmp/note-ids.txt | uniq -d | while read -r dup_id; do
    echo "   Duplicate ID: #$dup_id"
  done
fi

# Check 4: Verify IDs are sequential (allow gaps, just check ordering)
HIGHEST_ID=$(sort -n /tmp/note-ids.txt | tail -1)
echo "[INFO] Highest note ID: #$HIGHEST_ID"

# Check 5: Validate each note has required fields
while IFS= read -r note_id; do
  # Extract note section (from ### to next ---)
  NOTE_SECTION=$(awk "/^### #$note_id -/,/^---\$/" "$NOTES_FILE")

  # Check for required fields
  if ! echo "$NOTE_SECTION" | grep -q "**Created:**"; then
    echo "❌ Note #$note_id missing '**Created:**' field"
    ((ERRORS++))
  fi

  if ! echo "$NOTE_SECTION" | grep -q "**Status:**"; then
    echo "❌ Note #$note_id missing '**Status:**' field"
    ((ERRORS++))
  fi

  if ! echo "$NOTE_SECTION" | grep -q "**Description:**"; then
    echo "❌ Note #$note_id missing '**Description:**' field"
    ((ERRORS++))
  fi

  # Check status value is valid (open or closed)
  STATUS=$(echo "$NOTE_SECTION" | grep "**Status:**" | sed 's/\*\*Status:\*\* //')
  if [ "$STATUS" != "open" ] && [ "$STATUS" != "closed" ]; then
    echo "⚠️  Note #$note_id has invalid status: '$STATUS' (should be 'open' or 'closed')"
    ((WARNINGS++))
  fi

  # If status is closed, should have Closed field
  if [ "$STATUS" = "closed" ] && ! echo "$NOTE_SECTION" | grep -q "**Closed:**"; then
    echo "⚠️  Note #$note_id is closed but missing '**Closed:**' field"
    ((WARNINGS++))
  fi

done < /tmp/note-ids.txt

# Check 6: Verify header counts match actual counts
HEADER_OPEN_COUNT=$(grep "^## Open Notes" "$NOTES_FILE" | sed 's/.*(\([0-9]*\)).*/\1/' || echo 0)
ACTUAL_OPEN_COUNT=$(grep -c "^\*\*Status:\*\* open" "$NOTES_FILE" || echo 0)

if [ "$HEADER_OPEN_COUNT" != "$ACTUAL_OPEN_COUNT" ]; then
  echo "⚠️  Open notes count mismatch!"
  echo "   Header shows: $HEADER_OPEN_COUNT"
  echo "   Actually found: $ACTUAL_OPEN_COUNT"
  ((WARNINGS++))
fi

# Cleanup
rm -f /tmp/note-ids.txt

# --- Summary ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Validation Summary:"
echo "  Total notes: $NOTES_COUNT"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -gt 0 ]; then
  echo "❌ Validation FAILED - notes.md has structural errors"
  echo "   Run 'note-tracker' agent to rebuild structure"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo "⚠️  Validation PASSED with warnings - notes.md is usable but has minor issues"
  exit 0
else
  echo "✅ Validation PASSED - notes.md structure is correct"
  exit 0
fi
