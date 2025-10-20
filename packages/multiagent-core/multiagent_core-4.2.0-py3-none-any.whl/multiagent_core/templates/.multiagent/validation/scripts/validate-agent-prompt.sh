#!/usr/bin/env bash
# Script: validate-agent-prompt.sh
# Purpose: Check agent definition structure (mechanical checks only, no intelligence)
# Subsystem: validation
# Called by: /validation:validate command
# Outputs: JSON validation report

set -euo pipefail

# --- Configuration ---
AGENT_FILE="${1:-}"
OUTPUT_FILE="${2:-/tmp/agent-validation.json}"

# --- Usage ---
if [ -z "$AGENT_FILE" ]; then
  echo "Usage: $0 <agent-file> [output-file]"
  echo "Example: $0 ~/.claude/agents/backend-tester.md /tmp/validation.json"
  exit 1
fi

# --- Validation Checks (100% Mechanical) ---

echo "[INFO] Validating agent: $AGENT_FILE"

# Check 1: File exists
if [ ! -f "$AGENT_FILE" ]; then
  cat > "$OUTPUT_FILE" <<EOF
{
  "status": "failed",
  "agent": "$AGENT_FILE",
  "error": "File does not exist",
  "checks": {}
}
EOF
  exit 1
fi

# Initialize results
ISSUES=()
WARNINGS=()
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Check 2: YAML frontmatter exists (lines 1-5 should contain ---)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if head -5 "$AGENT_FILE" | grep -q "^---$"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  ISSUES+=("Missing YAML frontmatter (no --- found in first 5 lines)")
fi

# Check 3: model field present
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -q "^model:" "$AGENT_FILE"; then
  MODEL_VALUE=$(grep "^model:" "$AGENT_FILE" | head -1 | awk '{print $2}')

  # Check if it's the correct model
  if [ "$MODEL_VALUE" = "claude-sonnet-4-5-20250929" ]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    WARNINGS+=("Model is '$MODEL_VALUE', expected 'claude-sonnet-4-5-20250929'")
  fi
else
  ISSUES+=("Missing 'model:' field in frontmatter")
fi

# Check 4: tools array present
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -q "^tools:" "$AGENT_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  ISSUES+=("Missing 'tools:' field in frontmatter")
fi

# Check 5: File length (should not be >200 lines - agents should be concise)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
LINE_COUNT=$(wc -l < "$AGENT_FILE")
if [ "$LINE_COUNT" -le 200 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("Agent file is $LINE_COUNT lines (>200 lines may indicate verbosity)")
fi

# Check 6: No hardcoded absolute paths
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "^[^#]*/home/|^[^#]*/Users/" "$AGENT_FILE"; then
  ISSUES+=("Contains hardcoded absolute paths (/home/ or /Users/)")
else
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# Check 7: Structured prompt sections (optional but recommended)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -qE "<background>|<instructions>|<examples>" "$AGENT_FILE"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("No structured prompt sections found (<background>, <instructions>, <examples>)")
fi

# Check 8: Description is not multi-paragraph (should be concise)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
DESCRIPTION_START=$(grep -n "^---$" "$AGENT_FILE" | tail -1 | cut -d: -f1)
if [ -n "$DESCRIPTION_START" ]; then
  DESCRIPTION_SECTION=$(tail -n +$((DESCRIPTION_START + 1)) "$AGENT_FILE" | head -20)
  PARAGRAPH_COUNT=$(echo "$DESCRIPTION_SECTION" | grep -c "^$" || true)

  if [ "$PARAGRAPH_COUNT" -le 2 ]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    WARNINGS+=("Description appears verbose ($PARAGRAPH_COUNT paragraph breaks in first 20 lines)")
  fi
else
  WARNINGS+=("Could not determine description section")
fi

# --- Calculate Score ---
if [ "$CHECKS_TOTAL" -gt 0 ]; then
  SCORE=$(echo "scale=1; ($CHECKS_PASSED / $CHECKS_TOTAL) * 100" | bc)
else
  SCORE=0
fi

# Determine overall status
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
  "agent": "$AGENT_FILE",
  "score": $SCORE,
  "checks_passed": $CHECKS_PASSED,
  "checks_total": $CHECKS_TOTAL,
  "line_count": $LINE_COUNT,
  "model": "${MODEL_VALUE:-not_found}",
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

# Exit with appropriate code
if [ "$STATUS" = "failed" ]; then
  exit 1
elif [ "$STATUS" = "warning" ]; then
  exit 0
else
  exit 0
fi
