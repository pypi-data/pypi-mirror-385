#!/usr/bin/env bash
# Script: validate-frontmatter.sh
# Purpose: Verify YAML frontmatter structure in markdown files (mechanical only)
# Subsystem: validation
# Called by: /validation:validate command
# Outputs: JSON validation report

set -euo pipefail

# --- Configuration ---
FILE="${1:-}"
EXPECTED_FIELDS="${2:-}"  # Comma-separated list of required fields
OUTPUT_FILE="${3:-/tmp/frontmatter-validation.json}"

# --- Usage ---
if [ -z "$FILE" ]; then
  echo "Usage: $0 <file> [expected-fields] [output-file]"
  echo ""
  echo "Validates YAML frontmatter in markdown files."
  echo ""
  echo "Examples:"
  echo "  $0 ~/.claude/agents/backend-tester.md 'model,tools'"
  echo "  $0 ~/.claude/commands/testing/test.md 'name,description'"
  exit 1
fi

# --- Validation ---

echo "[INFO] Validating frontmatter: $FILE"

if [ ! -f "$FILE" ]; then
  cat > "$OUTPUT_FILE" <<EOF
{
  "status": "failed",
  "file": "$FILE",
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

# Check 1: Frontmatter exists (starts with ---)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if head -1 "$FILE" | grep -q "^---$"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  ISSUES+=("File does not start with YAML frontmatter delimiter (---)")
  # Can't continue without frontmatter
  cat > "$OUTPUT_FILE" <<EOF
{
  "status": "failed",
  "file": "$FILE",
  "score": 0,
  "checks_passed": 0,
  "checks_total": $CHECKS_TOTAL,
  "issues": ["File does not start with YAML frontmatter delimiter (---)"],
  "warnings": []
}
EOF
  echo "❌ No frontmatter found"
  exit 1
fi

# Check 2: Frontmatter is closed (second --- exists)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
CLOSING_LINE=$(awk '/^---$/{if(++count==2){print NR; exit}}' "$FILE")

if [ -n "$CLOSING_LINE" ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  FRONTMATTER_END=$CLOSING_LINE
else
  ISSUES+=("YAML frontmatter is not closed (missing second ---)")
  FRONTMATTER_END=100  # Assume it's somewhere in first 100 lines
fi

# Extract frontmatter content
FRONTMATTER=$(sed -n "2,${FRONTMATTER_END}p" "$FILE" | sed '$d')

# Check 3: Expected fields present
if [ -n "$EXPECTED_FIELDS" ]; then
  IFS=',' read -ra FIELDS <<< "$EXPECTED_FIELDS"
  for field in "${FIELDS[@]}"; do
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if echo "$FRONTMATTER" | grep -q "^$field:"; then
      CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
      ISSUES+=("Required field '$field:' not found in frontmatter")
    fi
  done
fi

# Check 4: No duplicate keys
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
KEYS=$(echo "$FRONTMATTER" | grep -E "^[a-z_]+:" | cut -d: -f1 | sort)
UNIQUE_KEYS=$(echo "$KEYS" | sort -u)

if [ "$(echo "$KEYS" | wc -l)" -eq "$(echo "$UNIQUE_KEYS" | wc -l)" ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("Duplicate keys found in frontmatter")
fi

# Check 5: Valid YAML syntax (basic check - indentation)
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
# Check for obvious syntax errors: tabs, unmatched brackets
if echo "$FRONTMATTER" | grep -q $'\t'; then
  WARNINGS+=("Frontmatter contains tabs (YAML requires spaces)")
else
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# Check 6: No empty values
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if echo "$FRONTMATTER" | grep -qE "^[a-z_]+:\s*$"; then
  WARNINGS+=("Some fields have empty values")
else
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# Check 7: Reasonable frontmatter length
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
FRONTMATTER_LINES=$(echo "$FRONTMATTER" | wc -l)
if [ "$FRONTMATTER_LINES" -le 50 ]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  WARNINGS+=("Frontmatter is $FRONTMATTER_LINES lines (>50 may indicate verbosity)")
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

# --- Extract field values ---
FIELDS_JSON=""
if [ -n "$EXPECTED_FIELDS" ]; then
  IFS=',' read -ra FIELDS <<< "$EXPECTED_FIELDS"
  FIELD_VALUES=()
  for field in "${FIELDS[@]}"; do
    VALUE=$(echo "$FRONTMATTER" | grep "^$field:" | head -1 | sed "s/^$field:\s*//" | tr -d '"' || echo "")
    FIELD_VALUES+=("\"$field\": \"$VALUE\"")
  done
  FIELDS_JSON=$(printf '%s' "${FIELD_VALUES[@]}" | paste -sd ',' -)
fi

# --- Generate Output ---
cat > "$OUTPUT_FILE" <<EOF
{
  "status": "$STATUS",
  "file": "$FILE",
  "score": $SCORE,
  "checks_passed": $CHECKS_PASSED,
  "checks_total": $CHECKS_TOTAL,
  "frontmatter_lines": $FRONTMATTER_LINES,
  "fields": {
    $FIELDS_JSON
  },
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
