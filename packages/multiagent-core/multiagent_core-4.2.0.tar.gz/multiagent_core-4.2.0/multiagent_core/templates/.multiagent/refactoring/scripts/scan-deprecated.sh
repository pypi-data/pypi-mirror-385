#!/usr/bin/env bash
# Script: scan-deprecated.sh
# Purpose: Scans codebase for usage of deprecated APIs and old patterns
# Subsystem: refactoring
# Called by: /refactoring:refactor slash command
# Outputs: JSON file with deprecated pattern locations

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/deprecated.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Scanning for deprecated patterns in: $PROJECT_DIR"

# Define patterns to search for (mechanical pattern matching)
# The agent will analyze the results intelligently

declare -A PATTERNS=(
  # JavaScript/TypeScript patterns
  ["callbacks"]='function.*\(.*callback|\.then\('
  ["var_declarations"]='^\s*var\s+\w+'
  ["class_components"]='class\s+\w+\s+extends\s+(React\.)?Component'
  ["require_syntax"]='const\s+\w+\s*=\s*require\('

  # Python patterns
  ["print_statements"]='^\s*print\s+'  # Python 2 print
  ["old_string_format"]='%s|%d|%f'     # Old % formatting

  # SQL patterns
  ["n_plus_one"]='forEach.*SELECT|map.*query|for.*SELECT'

  # General patterns
  ["todo_comments"]='TODO|FIXME|XXX|HACK'
  ["commented_code"]='^\s*#.*=|^\s*//.*=|^\s*/\*.*\*/'
)

# Find source files
SOURCE_FILES=$(find . -type f \( -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.next/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" 2>/dev/null)

if [ -z "$SOURCE_FILES" ]; then
  echo "[WARN] No source files found to analyze"
  echo '{"deprecated_patterns": [], "total_files_scanned": 0}' > "$OUTPUT_FILE"
  exit 0
fi

FILE_COUNT=$(echo "$SOURCE_FILES" | wc -l)
echo "[INFO] Found $FILE_COUNT source files to analyze"

# Start JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "scan_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_dir": "$PROJECT_DIR",
  "total_files_scanned": $FILE_COUNT,
  "deprecated_patterns": [
EOF

FIRST=true

# Search for each pattern
for pattern_name in "${!PATTERNS[@]}"; do
  pattern="${PATTERNS[$pattern_name]}"

  echo "[INFO] Searching for pattern: $pattern_name"

  # Use grep to find matches (mechanical operation)
  MATCHES=$(echo "$SOURCE_FILES" | xargs grep -l -E "$pattern" 2>/dev/null || true)

  if [ -n "$MATCHES" ]; then
    MATCH_COUNT=$(echo "$MATCHES" | wc -l)

    if [ "$FIRST" = true ]; then
      FIRST=false
    else
      echo "," >> "$OUTPUT_FILE"
    fi

    cat >> "$OUTPUT_FILE" <<ENTRY
    {
      "pattern_name": "$pattern_name",
      "pattern_regex": "$pattern",
      "occurrences": $MATCH_COUNT,
      "files": [
$(echo "$MATCHES" | sed 's/^/        "/; s/$/",/' | sed '$ s/,$//')
      ]
    }
ENTRY
  fi
done

# Close JSON
cat >> "$OUTPUT_FILE" <<EOF

  ]
}
EOF

# Summary
PATTERN_COUNT=$(grep -c '"pattern_name"' "$OUTPUT_FILE" || echo "0")
TOTAL_OCCURRENCES=$(grep '"occurrences"' "$OUTPUT_FILE" | awk -F: '{sum += $2} END {print sum}' || echo "0")

echo "✅ Deprecated pattern scan complete"
echo "   Files scanned: $FILE_COUNT"
echo "   Pattern types found: $PATTERN_COUNT"
echo "   Total occurrences: $TOTAL_OCCURRENCES"
echo "   Output: $OUTPUT_FILE"

exit 0
