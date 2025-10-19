#!/usr/bin/env bash
# Script: scan-production-mocks.sh
# Purpose: Find test/mock code in production files
# Subsystem: testing
# Called by: /testing:test-prod slash command
# Outputs: List of files with mock code in production

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/production-mocks.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Scanning for mocks in production code: $PROJECT_DIR"

# Directories to scan (production code)
SCAN_DIRS=("src" "app" "lib" "backend" "api")

# Patterns to search for
MOCK_PATTERNS=(
  "mock"
  "fake"
  "dummy"
  "stub"
  "test"
  "__tests__"
  "jest.mock"
  "@testing-library"
)

# Files with mocks
MOCK_FILES=()

# Scan each directory
for DIR in "${SCAN_DIRS[@]}"; do
  if [ -d "$DIR" ]; then
    echo "[INFO] Scanning directory: $DIR"

    # Search for mock patterns
    for PATTERN in "${MOCK_PATTERNS[@]}"; do
      while IFS= read -r FILE; do
        if [ -n "$FILE" ]; then
          MOCK_FILES+=("$FILE:$PATTERN")
        fi
      done < <(grep -rl "$PATTERN" "$DIR" --exclude-dir=node_modules --exclude-dir=__tests__ 2>/dev/null || true)
    done
  fi
done

# Remove duplicates
MOCK_FILES=($(printf '%s\n' "${MOCK_FILES[@]}" | sort -u))

# Count issues
CRITICAL_COUNT=0
WARNING_COUNT=0

for ITEM in "${MOCK_FILES[@]}"; do
  FILE="${ITEM%%:*}"
  PATTERN="${ITEM##*:}"

  # Categorize severity
  if [[ "$PATTERN" == "mock" || "$PATTERN" == "fake" || "$PATTERN" == "dummy" ]]; then
    ((CRITICAL_COUNT++))
  else
    ((WARNING_COUNT++))
  fi
done

# Generate JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_directory": "$PROJECT_DIR",
  "total_issues": ${#MOCK_FILES[@]},
  "critical_issues": $CRITICAL_COUNT,
  "warning_issues": $WARNING_COUNT,
  "files_with_mocks": [
$(printf '    "%s"' "${MOCK_FILES[@]}" | sed 's/$/,/; $s/,$//')
  ]
}
EOF

if [ ${#MOCK_FILES[@]} -eq 0 ]; then
  echo "✅ No mocks found in production code"
else
  echo "⚠️  Found ${#MOCK_FILES[@]} files with potential mock code"
  echo "   Critical: $CRITICAL_COUNT"
  echo "   Warnings: $WARNING_COUNT"
fi
echo "[INFO] Output saved to: $OUTPUT_FILE"
exit 0
