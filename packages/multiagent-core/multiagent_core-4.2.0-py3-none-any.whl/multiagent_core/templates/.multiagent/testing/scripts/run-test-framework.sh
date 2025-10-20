#!/usr/bin/env bash
# Script: run-test-framework.sh
# Purpose: Execute appropriate test command based on project type
# Subsystem: testing
# Called by: /testing:test slash command
# Outputs: Test execution results

set -euo pipefail

# --- Configuration ---
PROJECT_TYPE_JSON="${1:-/tmp/project-type.json}"
PROJECT_DIR="${2:-.}"
TEST_FLAGS="${3:-}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Running tests for project in: $PROJECT_DIR"

# Detect test framework if project type JSON doesn't exist
if [ ! -f "$PROJECT_TYPE_JSON" ]; then
  echo "[WARN] Project type JSON not found, attempting auto-detection"

  # Try npm test first
  if [ -f "package.json" ]; then
    echo "[INFO] Running npm test..."
    npm test $TEST_FLAGS
    exit 0
  fi

  # Try pytest
  if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "[INFO] Running pytest..."
    pytest $TEST_FLAGS
    exit 0
  fi

  # Try go test
  if [ -f "go.mod" ]; then
    echo "[INFO] Running go test..."
    go test ./... $TEST_FLAGS
    exit 0
  fi

  echo "[ERROR] Could not detect test framework"
  exit 1
fi

# Read project type from JSON
PROJECT_TYPE=$(grep -oP '"project_type":\s*"\K[^"]+' "$PROJECT_TYPE_JSON" 2>/dev/null || echo "unknown")
BACKEND_FRAMEWORK=$(grep -oP '"backend_framework":\s*"\K[^"]+' "$PROJECT_TYPE_JSON" 2>/dev/null || echo "")

echo "[INFO] Project type: $PROJECT_TYPE"

# Run appropriate test command
case "$PROJECT_TYPE" in
  frontend|fullstack)
    if [ -f "package.json" ]; then
      echo "[INFO] Running frontend tests with npm..."
      npm test $TEST_FLAGS
    fi
    ;;
  backend)
    if [ "$BACKEND_FRAMEWORK" = "Python" ]; then
      echo "[INFO] Running backend tests with pytest..."
      pytest $TEST_FLAGS
    elif [ "$BACKEND_FRAMEWORK" = "Go" ]; then
      echo "[INFO] Running backend tests with go test..."
      go test ./... $TEST_FLAGS
    elif [ -f "package.json" ]; then
      echo "[INFO] Running backend tests with npm..."
      npm test $TEST_FLAGS
    fi
    ;;
  *)
    echo "[ERROR] Unknown project type: $PROJECT_TYPE"
    exit 1
    ;;
esac

echo "✅ Test execution completed"
exit 0
