#!/usr/bin/env bash
# Script: validate-test-coverage.sh
# Purpose: Check test coverage requirements are met
# Subsystem: testing
# Called by: /testing:test-generate slash command
# Outputs: Coverage validation report

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/coverage-report.json}"
MIN_COVERAGE="${3:-80}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Validating test coverage in: $PROJECT_DIR"

# Count test files
UNIT_TESTS=$(find __tests__/unit -name "*.test.*" 2>/dev/null | wc -l)
INTEGRATION_TESTS=$(find __tests__/integration -name "*.test.*" 2>/dev/null | wc -l)
E2E_TESTS=$(find __tests__/e2e -name "*.test.*" 2>/dev/null | wc -l)
TOTAL_TESTS=$((UNIT_TESTS + INTEGRATION_TESTS + E2E_TESTS))

# Count source files (estimate coverage)
SOURCE_FILES=0
if [ -d "src" ]; then
  SOURCE_FILES=$(find src -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" 2>/dev/null | wc -l)
elif [ -d "app" ]; then
  SOURCE_FILES=$(find app -name "*.py" 2>/dev/null | wc -l)
fi

# Calculate estimated coverage (rough estimate: 1 test per source file = 100%)
ESTIMATED_COVERAGE=0
if [ $SOURCE_FILES -gt 0 ]; then
  ESTIMATED_COVERAGE=$(awk "BEGIN {printf \"%.0f\", ($TOTAL_TESTS / $SOURCE_FILES) * 100}")
  if [ $ESTIMATED_COVERAGE -gt 100 ]; then
    ESTIMATED_COVERAGE=100
  fi
fi

# Determine pass/fail
STATUS="PASS"
if [ $ESTIMATED_COVERAGE -lt $MIN_COVERAGE ]; then
  STATUS="FAIL"
fi

# Generate JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_directory": "$PROJECT_DIR",
  "unit_tests": $UNIT_TESTS,
  "integration_tests": $INTEGRATION_TESTS,
  "e2e_tests": $E2E_TESTS,
  "total_tests": $TOTAL_TESTS,
  "source_files": $SOURCE_FILES,
  "estimated_coverage": $ESTIMATED_COVERAGE,
  "minimum_coverage": $MIN_COVERAGE,
  "status": "$STATUS"
}
EOF

if [ "$STATUS" = "PASS" ]; then
  echo "✅ Coverage validation passed: ${ESTIMATED_COVERAGE}% (minimum: ${MIN_COVERAGE}%)"
else
  echo "⚠️  Coverage validation failed: ${ESTIMATED_COVERAGE}% (minimum: ${MIN_COVERAGE}%)"
fi
echo "[INFO] Output saved to: $OUTPUT_FILE"
exit 0
