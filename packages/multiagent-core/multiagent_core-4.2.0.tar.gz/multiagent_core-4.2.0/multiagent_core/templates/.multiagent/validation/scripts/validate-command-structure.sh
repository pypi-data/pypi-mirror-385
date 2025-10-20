#!/usr/bin/env bash
# Script: validate-command-structure.sh
# Purpose: Verify command structure and orchestration purity (mechanical only)
# Subsystem: validation
# Called by: /validation:validate command
# Outputs: JSON validation report

set -euo pipefail

# --- Configuration ---
COMMAND_FILE="${1:-}"
OUTPUT_FILE="${2:-/tmp/command-validation.json}"

# --- Usage ---
if [ -z "$COMMAND_FILE" ]; then
  echo "Usage: $0 <command-file> [output-file]"
  echo "Example: $0 ~/.claude/commands/testing/test.md /tmp/validation.json"
  exit 1
fi

# --- Validation Checks ---

echo "[INFO] Validating command: $COMMAND_FILE"

if [ ! -f "$COMMAND_FILE" ]; then
  cat > "$OUTPUT_FILE" <<EOF
{
  "status": "failed",
  "command": "$COMMAND_FILE",
  "error": "File does not exist",
  "checks": {}
}
EOF
  exit 1
fi

ISSUES=()
WARNINGS=()
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Check 1: YAML frontmatter exists
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if head -10 "$COMMAND_FILE" | grep -q "^---$"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  ISSUES+=("Missing YAML frontmatter")
fi

# Check 2: File length (<80 lines for commands is ideal)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
LINE_COUNT=$(wc -l < "$COMMAND_FILE")
if [ "$LINE_COUNT" -le 80 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
elif [ "$LINE_COUNT" -le 120 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  WARNINGS+=("Command is $LINE_COUNT lines (>80 but <120, acceptable)")
else
  ISSUES+=("Command is $LINE_COUNT lines (should be <80 lines)")
fi

# Check 3: Embedded bash detection (commands should orchestrate, not execute)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
# Count lines that look like embedded bash
EMBEDDED_BASH_COUNT=$(grep -cE "^\s*(if |for |while |case |function |local |export |cd |mkdir |rm |cp |mv )" "$COMMAND_FILE" || true)

if [ "$EMBEDDED_BASH_COUNT" -eq 0 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
elif [ "$EMBEDDED_BASH_COUNT" -le 3 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  WARNINGS+=("Found $EMBEDDED_BASH_COUNT lines of embedded bash (minimal, acceptable)")
else
  ISSUES+=("Found $EMBEDDED_BASH_COUNT lines of embedded bash (should delegate to scripts)")
fi

# Check 4: SlashCommand() or Task() usage (proper orchestration)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "SlashCommand\(|Task\(" "$COMMAND_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("No SlashCommand() or Task() calls found (command may not be orchestrating)")
fi

# Check 5: Step numbering (workflow should be clear)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "^## (Step|Phase) [0-9]|^[0-9]+\. " "$COMMAND_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("No step numbering found (workflow may not be clear)")
fi

# Check 6: No hardcoded file paths
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "^[^#]*/home/|^[^#]*/Users/" "$COMMAND_FILE"; then
  ISSUES+=("Contains hardcoded absolute paths")
else
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# Check 7: Error handling present
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qiE "error|fail|exit|if.*not" "$COMMAND_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("No obvious error handling found")
fi

# Check 8: Script delegation (should call scripts for mechanical ops)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "\.sh |scripts/" "$COMMAND_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("No script delegation found (may be doing mechanical work inline)")
fi

# --- Calculate Score ---
if [ "$CHECKS_TOTAL" -gt 0 ]; then
  SCORE=$(echo "scale=1; ($CHECKS_PASSED / $CHECKS_TOTAL) * 100" | bc)
else
  SCORE=0
fi

# Determine status
if [ "${#ISSUES[@]}" -eq 0 ]; then
  STATUS="passed"
elif [ "$CHECKS_PASSED" -ge $((CHECKS_TOTAL * 70 / 100)) ]; then
  STATUS="warning"
else
  STATUS="failed"
fi

# --- Generate Output ---
cat > "$OUTPUT_FILE" <<EOF
{
  "status": "$STATUS",
  "command": "$COMMAND_FILE",
  "score": $SCORE,
  "checks_passed": $CHECKS_PASSED,
  "checks_total": $CHECKS_TOTAL,
  "line_count": $LINE_COUNT,
  "embedded_bash_lines": $EMBEDDED_BASH_COUNT,
  "issues": [
$(printf '    "%s"' "${ISSUES[@]}" | paste -sd ',' -)
  ],
  "warnings": [
$(printf '    "%s"' "${WARNINGS[@]}" | paste -sd ',' -)
  ]
}
EOF

echo "✅ Validation complete: $STATUS (${CHECKS_PASSED}/${CHECKS_TOTAL} checks passed)"
echo "📄 Report: $OUTPUT_FILE"

if [ "$STATUS" = "failed" ]; then
  exit 1
else
  exit 0
fi
