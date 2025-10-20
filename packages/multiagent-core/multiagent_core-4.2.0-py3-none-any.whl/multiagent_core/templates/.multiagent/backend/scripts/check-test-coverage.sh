#!/usr/bin/env bash
# Script: check-test-coverage.sh
# Purpose: Validate backend test files exist for implemented features
# Subsystem: backend
# Called by: /backend:test slash command
# Outputs: Test coverage report to stdout

set -euo pipefail

# --- Configuration ---
SPEC_DIR="${1:-.}"
TEST_DIR="${2:-tests/backend}"

# --- Main Logic ---
echo "[INFO] Checking backend test coverage for $SPEC_DIR"

# Check if test directory exists
if [ ! -d "$TEST_DIR" ]; then
  echo "⚠️  Test directory not found: $TEST_DIR"
  echo "   Create test structure: mkdir -p $TEST_DIR/{unit,integration}"
  exit 0
fi

# Count test files
UNIT_TESTS=$(find "$TEST_DIR/unit" -name "*.test.*" -o -name "test_*.py" 2>/dev/null | wc -l)
INTEGRATION_TESTS=$(find "$TEST_DIR/integration" -name "*.test.*" -o -name "test_*.py" 2>/dev/null | wc -l)
TOTAL_TESTS=$((UNIT_TESTS + INTEGRATION_TESTS))

# --- Output ---
echo "✅ Test Coverage Summary:"
echo "   Unit tests: $UNIT_TESTS"
echo "   Integration tests: $INTEGRATION_TESTS"
echo "   Total tests: $TOTAL_TESTS"

if [ $TOTAL_TESTS -eq 0 ]; then
  echo "⚠️  No tests found. Run /backend:test $SPEC_DIR to create tests."
fi

exit 0
