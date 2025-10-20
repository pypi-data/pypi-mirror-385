#!/usr/bin/env bash
# Script: validate-idea.sh
# Purpose: Validates idea file structure and metadata
# Subsystem: idea
# Called by: /idea:create, /idea:promote commands
# Outputs: Exit code 0 (valid) or 1 (invalid) with error messages

set -euo pipefail

# --- Configuration ---
IDEA_FILE="${1:-}"

# --- Validation ---
if [[ -z "$IDEA_FILE" ]]; then
  echo "❌ Error: Idea file path required"
  echo "Usage: validate-idea.sh <path-to-idea.md>"
  exit 1
fi

if [[ ! -f "$IDEA_FILE" ]]; then
  echo "❌ Error: File not found: $IDEA_FILE"
  exit 1
fi

echo "[INFO] Validating idea file: $IDEA_FILE"

VALIDATION_FAILED=0

# --- Check Required Sections ---
REQUIRED_SECTIONS=("Problem" "Proposed Solution" "Rough Notes" "When to Build")

for section in "${REQUIRED_SECTIONS[@]}"; do
  if ! grep -q "^## $section" "$IDEA_FILE"; then
    echo "❌ Missing required section: ## $section"
    VALIDATION_FAILED=1
  fi
done

# --- Check Required Metadata ---
if ! grep -q "^\*\*Created\*\*:" "$IDEA_FILE"; then
  echo "❌ Missing metadata: Created"
  VALIDATION_FAILED=1
fi

if ! grep -q "^\*\*Complexity\*\*:" "$IDEA_FILE"; then
  echo "❌ Missing metadata: Complexity"
  VALIDATION_FAILED=1
fi

if ! grep -q "^\*\*Value\*\*:" "$IDEA_FILE"; then
  echo "❌ Missing metadata: Value"
  VALIDATION_FAILED=1
fi

if ! grep -q "^\*\*Category\*\*:" "$IDEA_FILE"; then
  echo "❌ Missing metadata: Category"
  VALIDATION_FAILED=1
fi

# --- Validate Metadata Values ---
COMPLEXITY=$(grep "^\*\*Complexity\*\*:" "$IDEA_FILE" | sed 's/.*: //' | awk '{print $1}')
if [[ ! "$COMPLEXITY" =~ ^(simple|medium|complex)$ ]]; then
  echo "❌ Invalid Complexity value: '$COMPLEXITY' (must be simple, medium, or complex)"
  VALIDATION_FAILED=1
fi

VALUE=$(grep "^\*\*Value\*\*:" "$IDEA_FILE" | sed 's/.*: //' | awk '{print $1}')
if [[ ! "$VALUE" =~ ^(low|medium|high)$ ]]; then
  echo "❌ Invalid Value: '$VALUE' (must be low, medium, or high)"
  VALIDATION_FAILED=1
fi

CATEGORY=$(grep "^\*\*Category\*\*:" "$IDEA_FILE" | sed 's/.*: //' | awk '{print $1}')
if [[ ! "$CATEGORY" =~ ^(feature|improvement|infrastructure|integration)$ ]]; then
  echo "❌ Invalid Category: '$CATEGORY' (must be feature, improvement, infrastructure, or integration)"
  VALIDATION_FAILED=1
fi

# --- Report Results ---
if [ $VALIDATION_FAILED -eq 1 ]; then
  echo ""
  echo "❌ Validation FAILED"
  echo "Fix the issues above and try again"
  exit 1
else
  echo ""
  echo "✅ Validation PASSED"
  echo "Idea file is valid and ready for use"
  exit 0
fi
