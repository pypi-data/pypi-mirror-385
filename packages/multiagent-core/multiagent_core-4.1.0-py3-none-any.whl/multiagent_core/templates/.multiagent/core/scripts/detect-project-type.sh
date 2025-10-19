#!/usr/bin/env bash
# Script: detect-project-type.sh
# Purpose: Infer project type from spec.md keywords
# Subsystem: core
# Called by: project-analyzer agent
# Outputs: Text file with detected project type

set -euo pipefail

SPEC_FILE="${1}"
OUTPUT_FILE="${2:-/tmp/detected-type.txt}"

echo "[INFO] Detecting project type from spec..."

# Validate spec file exists
if [[ ! -f $SPEC_FILE ]]; then
  echo "ERROR: Spec file not found: $SPEC_FILE"
  exit 1
fi

# Read and normalize content
CONTENT=$(cat "$SPEC_FILE" | tr '[:upper:]' '[:lower:]')

# Detect project type based on keywords (order matters - most specific first)
if echo "$CONTENT" | grep -qE "(saas|microservices|enterprise|multi-tenant)"; then
  TYPE="saas"
elif echo "$CONTENT" | grep -qE "(ai|intelligent|llm|vector|machine learning|ml model)"; then
  TYPE="ai-app"
elif echo "$CONTENT" | grep -qE "(app|platform|dashboard|backend|api|database|full-stack|full stack)"; then
  TYPE="web-app"
elif echo "$CONTENT" | grep -qE "(website|marketing|blog|cms|content)"; then
  TYPE="website"
elif echo "$CONTENT" | grep -qE "(landing|one-page|single page|portfolio|static)"; then
  TYPE="landing-page"
else
  TYPE="web-app"  # Default to web-app if unclear
fi

echo "$TYPE" > "$OUTPUT_FILE"
echo "✅ Detected type: $TYPE"
exit 0
