#!/usr/bin/env bash
# Script: scan-code-notes.sh
# Purpose: Scan codebase for TODO/FIXME/BUG/NOTE comments
# Subsystem: notes
# Called by: note-analyzer agent
# Outputs: JSON list of inline code comments

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/code-notes-scan.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Scanning codebase for inline notes (TODO, FIXME, BUG, NOTE)..."

# Initialize JSON output
cat > "$OUTPUT_FILE" <<'EOF'
{
  "scan_timestamp": "",
  "project_dir": "",
  "total_comments": 0,
  "by_type": {
    "TODO": 0,
    "FIXME": 0,
    "BUG": 0,
    "NOTE": 0
  },
  "comments": []
}
EOF

# Find all source files (exclude node_modules, .git, dist, build)
TEMP_RESULTS="/tmp/code-notes-results.txt"
> "$TEMP_RESULTS"

# Search patterns for different comment types
# Supports: // TODO, /* TODO */, # TODO, <!-- TODO -->
grep -rn --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" \
         --include="*.py" --include="*.rb" --include="*.go" --include="*.java" \
         --include="*.c" --include="*.cpp" --include="*.h" --include="*.hpp" \
         --include="*.rs" --include="*.sh" --include="*.bash" \
         --include="*.html" --include="*.css" --include="*.scss" \
         --exclude-dir="node_modules" --exclude-dir=".git" \
         --exclude-dir="dist" --exclude-dir="build" --exclude-dir="vendor" \
         -E "(//|/\*|#|<!--)\s*(TODO|FIXME|BUG|NOTE):" . \
         2>/dev/null >> "$TEMP_RESULTS" || true

# Count results by type (grep -c returns 0 if no matches, no need for || echo 0)
TODO_COUNT=$(grep -ic "TODO:" "$TEMP_RESULTS" 2>/dev/null)
FIXME_COUNT=$(grep -ic "FIXME:" "$TEMP_RESULTS" 2>/dev/null)
BUG_COUNT=$(grep -ic "BUG:" "$TEMP_RESULTS" 2>/dev/null)
NOTE_COUNT=$(grep -ic "NOTE:" "$TEMP_RESULTS" 2>/dev/null)
TOTAL_COUNT=$((TODO_COUNT + FIXME_COUNT + BUG_COUNT + NOTE_COUNT))

# Build JSON (simple approach, not parsing individual comments for now)
cat > "$OUTPUT_FILE" <<EOF
{
  "scan_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_dir": "$PROJECT_DIR",
  "total_comments": $TOTAL_COUNT,
  "by_type": {
    "TODO": $TODO_COUNT,
    "FIXME": $FIXME_COUNT,
    "BUG": $BUG_COUNT,
    "NOTE": $NOTE_COUNT
  },
  "results_file": "$TEMP_RESULTS"
}
EOF

echo "✅ Code scan complete"
echo "   Found $TOTAL_COUNT inline comments:"
echo "   - TODO: $TODO_COUNT"
echo "   - FIXME: $FIXME_COUNT"
echo "   - BUG: $BUG_COUNT"
echo "   - NOTE: $NOTE_COUNT"
echo ""
echo "   Results: $OUTPUT_FILE"
echo "   Details: $TEMP_RESULTS"

exit 0
