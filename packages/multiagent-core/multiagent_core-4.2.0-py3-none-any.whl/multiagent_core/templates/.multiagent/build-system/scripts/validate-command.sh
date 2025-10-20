#!/usr/bin/env bash
# Script: validate-command.sh
# Purpose: Validate slash command file compliance with framework standards
# Subsystem: build-system
# Called by: /build:slash-command command after generation
# Outputs: Validation report to stdout

set -euo pipefail

COMMAND_FILE="${1:?Usage: $0 <command-file>}"

echo "[INFO] Validating command file: $COMMAND_FILE"

# Check file exists
if [[ ! -f "$COMMAND_FILE" ]]; then
    echo "❌ ERROR: File not found: $COMMAND_FILE"
    exit 1
fi

# Check frontmatter exists
if ! grep -q "^---$" "$COMMAND_FILE"; then
    echo "❌ ERROR: Missing frontmatter"
    exit 1
fi

# Check required frontmatter fields
REQUIRED_FIELDS=("allowed-tools:" "description:")
for field in "${REQUIRED_FIELDS[@]}"; do
    if ! grep -q "^$field" "$COMMAND_FILE"; then
        echo "❌ ERROR: Missing required field: $field"
        exit 1
    fi
done

# Check file length (should be under 60 lines)
LINE_COUNT=$(wc -l < "$COMMAND_FILE")
if ((LINE_COUNT > 60)); then
    echo "⚠️  WARNING: Command file is $LINE_COUNT lines (target: under 60)"
fi

# Check for Task invocation
if ! grep -q "Invoke the" "$COMMAND_FILE"; then
    echo "⚠️  WARNING: No subagent invocation found - should use Task tool"
fi

echo "✅ Command validation passed"
exit 0
