#!/usr/bin/env bash
# Script: parse-tasks-for-tests.sh
# Purpose: Extract testable items from tasks.md or layered-tasks.md
# Subsystem: testing
# Called by: /testing:test-generate slash command
# Outputs: JSON file with testable items categorized by type

set -euo pipefail

# --- Configuration ---
SPEC_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/testable-items.json}"

# --- Main Logic ---
cd "$SPEC_DIR" || exit 1

echo "[INFO] Parsing tasks from spec directory: $SPEC_DIR"

# Check for layered-tasks.md first (preferred), fallback to tasks.md
TASKS_FILE=""
if [ -f "agent-tasks/layered-tasks.md" ]; then
  TASKS_FILE="agent-tasks/layered-tasks.md"
  echo "[INFO] Found layered-tasks.md"
elif [ -f "tasks.md" ]; then
  TASKS_FILE="tasks.md"
  echo "[INFO] Found tasks.md"
else
  echo "[ERROR] No tasks file found in $SPEC_DIR"
  exit 1
fi

# Extract tasks and categorize them
# Look for task patterns: - [ ] or - [x] followed by task description
# Categorize by keywords: API, component, util, service, etc.

UNIT_TESTS=()
INTEGRATION_TESTS=()
E2E_TESTS=()

# Parse tasks and categorize
while IFS= read -r line; do
  # Match task lines
  if echo "$line" | grep -qE '^\s*-\s+\[[ x]\]'; then
    # Extract task description
    TASK_DESC=$(echo "$line" | sed -E 's/^\s*-\s+\[[ x]\]\s*//')

    # Categorize by keywords
    if echo "$TASK_DESC" | grep -qiE 'component|ui|button|form|page'; then
      UNIT_TESTS+=("$TASK_DESC")
    elif echo "$TASK_DESC" | grep -qiE 'api|endpoint|route|service'; then
      INTEGRATION_TESTS+=("$TASK_DESC")
    elif echo "$TASK_DESC" | grep -qiE 'workflow|journey|e2e|end-to-end|integration'; then
      E2E_TESTS+=("$TASK_DESC")
    else
      # Default to unit test
      UNIT_TESTS+=("$TASK_DESC")
    fi
  fi
done < "$TASKS_FILE"

# Generate JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "spec_directory": "$SPEC_DIR",
  "tasks_file": "$TASKS_FILE",
  "unit_tests": [
$(printf '    "%s"' "${UNIT_TESTS[@]}" | sed 's/$/,/; $s/,$//')
  ],
  "integration_tests": [
$(printf '    "%s"' "${INTEGRATION_TESTS[@]}" | sed 's/$/,/; $s/,$//')
  ],
  "e2e_tests": [
$(printf '    "%s"' "${E2E_TESTS[@]}" | sed 's/$/,/; $s/,$//')
  ],
  "total_testable_items": $((${#UNIT_TESTS[@]} + ${#INTEGRATION_TESTS[@]} + ${#E2E_TESTS[@]}))
}
EOF

echo "✅ Parsed ${#UNIT_TESTS[@]} unit tests, ${#INTEGRATION_TESTS[@]} integration tests, ${#E2E_TESTS[@]} e2e tests"
echo "[INFO] Output saved to: $OUTPUT_FILE"
exit 0
