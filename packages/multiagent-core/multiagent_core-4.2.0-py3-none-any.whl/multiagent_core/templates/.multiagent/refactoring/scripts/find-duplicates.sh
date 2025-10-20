#!/usr/bin/env bash
# Script: find-duplicates.sh
# Purpose: Detects duplicate code blocks across the codebase using simple pattern matching
# Subsystem: refactoring
# Called by: /refactoring:refactor slash command
# Outputs: JSON file with duplicate code block locations

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/duplicates.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Scanning for duplicate code blocks in: $PROJECT_DIR"

# Find source files (adjust extensions based on project)
SOURCE_FILES=$(find . -type f \( -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.next/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" 2>/dev/null)

if [ -z "$SOURCE_FILES" ]; then
  echo "[WARN] No source files found to analyze"
  echo '{"duplicates": [], "total_files_scanned": 0}' > "$OUTPUT_FILE"
  exit 0
fi

FILE_COUNT=$(echo "$SOURCE_FILES" | wc -l)
echo "[INFO] Found $FILE_COUNT source files to analyze"

# Use simple hash-based duplicate detection
# For each file, generate a hash of code blocks (functions, methods)
# This is mechanical - the agent will do the intelligent analysis

echo "[INFO] Generating code block hashes..."

# Create temporary file for hashes
HASH_FILE=$(mktemp)

# Simple approach: hash each file's content
# (A more sophisticated tool like jscpd or PMD would be better for production)
while IFS= read -r file; do
  # Generate hash of file content (simplified duplicate detection)
  HASH=$(md5sum "$file" 2>/dev/null | awk '{print $1}')
  echo "$HASH|$file" >> "$HASH_FILE"
done <<< "$SOURCE_FILES"

# Find duplicate hashes
DUPLICATES=$(sort "$HASH_FILE" | uniq -d -w 32)

# Build JSON output
echo "[INFO] Building duplicate report..."

cat > "$OUTPUT_FILE" <<EOF
{
  "scan_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_dir": "$PROJECT_DIR",
  "total_files_scanned": $FILE_COUNT,
  "duplicates": [
EOF

# Add duplicate entries
FIRST=true
if [ -n "$DUPLICATES" ]; then
  while IFS='|' read -r hash file; do
    # Find all files with this hash
    MATCHING_FILES=$(grep "^$hash" "$HASH_FILE" | cut -d'|' -f2)
    MATCH_COUNT=$(echo "$MATCHING_FILES" | wc -l)

    if [ "$MATCH_COUNT" -gt 1 ]; then
      if [ "$FIRST" = true ]; then
        FIRST=false
      else
        echo "," >> "$OUTPUT_FILE"
      fi

      cat >> "$OUTPUT_FILE" <<ENTRY
    {
      "hash": "$hash",
      "occurrences": $MATCH_COUNT,
      "files": [
$(echo "$MATCHING_FILES" | sed 's/^/        "/; s/$/",/' | sed '$ s/,$//')
      ]
    }
ENTRY
    fi
  done <<< "$DUPLICATES"
fi

# Close JSON
cat >> "$OUTPUT_FILE" <<EOF

  ]
}
EOF

# Cleanup
rm -f "$HASH_FILE"

# Summary
DUPLICATE_COUNT=$(grep -c '"hash"' "$OUTPUT_FILE" || echo "0")
echo "✅ Duplicate detection complete"
echo "   Files scanned: $FILE_COUNT"
echo "   Duplicate patterns found: $DUPLICATE_COUNT"
echo "   Output: $OUTPUT_FILE"

exit 0
