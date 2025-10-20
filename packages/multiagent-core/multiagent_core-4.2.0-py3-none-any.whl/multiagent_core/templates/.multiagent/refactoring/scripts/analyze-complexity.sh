#!/usr/bin/env bash
# Script: analyze-complexity.sh
# Purpose: Identifies overly complex functions using simple metrics
# Subsystem: refactoring
# Called by: /refactoring:refactor slash command
# Outputs: JSON file with complexity metrics

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/complexity.json}"

# Complexity thresholds (configurable)
MAX_LINES_PER_FUNCTION=50
MAX_NESTING_DEPTH=3
MAX_PARAMETERS=5

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Analyzing code complexity in: $PROJECT_DIR"

# Find source files
SOURCE_FILES=$(find . -type f \( -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.py" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.next/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" 2>/dev/null)

if [ -z "$SOURCE_FILES" ]; then
  echo "[WARN] No source files found to analyze"
  echo '{"complex_functions": [], "total_files_scanned": 0}' > "$OUTPUT_FILE"
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
  "complexity_thresholds": {
    "max_lines_per_function": $MAX_LINES_PER_FUNCTION,
    "max_nesting_depth": $MAX_NESTING_DEPTH,
    "max_parameters": $MAX_PARAMETERS
  },
  "complex_functions": [
EOF

FIRST=true
COMPLEX_COUNT=0

# Simple complexity detection (mechanical)
# Real complexity analysis would use AST parsing, but this provides basic heuristics

while IFS= read -r file; do
  # Count lines per file (rough indicator)
  LINE_COUNT=$(wc -l < "$file")

  # Flag very long files as potentially complex
  if [ "$LINE_COUNT" -gt 500 ]; then
    if [ "$FIRST" = true ]; then
      FIRST=false
    else
      echo "," >> "$OUTPUT_FILE"
    fi

    # Count deeply nested blocks (simple heuristic: count indentation)
    MAX_INDENT=$(awk '{print gsub(/    /, "")}' "$file" | sort -nr | head -1)

    # Count function definitions (rough estimate)
    FUNCTION_COUNT=$(grep -c -E 'function |def |func ' "$file" 2>/dev/null || echo "0")

    cat >> "$OUTPUT_FILE" <<ENTRY
    {
      "file": "$file",
      "total_lines": $LINE_COUNT,
      "max_nesting_depth": ${MAX_INDENT:-0},
      "function_count": $FUNCTION_COUNT,
      "complexity_score": $(( (LINE_COUNT / 100) + (MAX_INDENT * 2) )),
      "issues": [
$([ "$LINE_COUNT" -gt 500 ] && echo '        "file_too_long",' || true)
$([ "${MAX_INDENT:-0}" -gt "$MAX_NESTING_DEPTH" ] && echo '        "deep_nesting",' || true | sed '$ s/,$//')
      ]
    }
ENTRY

    COMPLEX_COUNT=$((COMPLEX_COUNT + 1))
  fi
done <<< "$SOURCE_FILES"

# Close JSON
cat >> "$OUTPUT_FILE" <<EOF

  ],
  "summary": {
    "total_complex_files": $COMPLEX_COUNT,
    "files_over_500_lines": $COMPLEX_COUNT
  }
}
EOF

echo "✅ Complexity analysis complete"
echo "   Files scanned: $FILE_COUNT"
echo "   Complex files found: $COMPLEX_COUNT"
echo "   Output: $OUTPUT_FILE"

exit 0
