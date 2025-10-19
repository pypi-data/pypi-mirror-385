#!/usr/bin/env bash
# Script: validate-prerequisites.sh
# Purpose: Check that all prerequisites are met for project setup
# Subsystem: core
# Called by: project-analyzer agent
# Outputs: Exit code (0=success, 1=failure)

set -euo pipefail

PROJECT_DIR="${1:-.}"

cd "$PROJECT_DIR" || exit 1

echo "[INFO] Validating prerequisites..."

ERRORS=0

# Check .multiagent/ exists
if [[ ! -d .multiagent ]]; then
  echo "❌ ERROR: .multiagent/ directory not found (run 'multiagent init')"
  ERRORS=$((ERRORS + 1))
fi

# Check spec exists
if ! ls specs/001-*/spec.md &>/dev/null 2>&1; then
  echo "❌ ERROR: No spec file found in specs/ (run '/specify')"
  ERRORS=$((ERRORS + 1))
fi

# Check git repository
if [[ ! -d .git ]]; then
  echo "⚠️  WARNING: Not a git repository (recommended to run 'git init')"
fi

if [[ $ERRORS -gt 0 ]]; then
  echo "❌ Prerequisite validation failed with $ERRORS error(s)"
  exit 1
fi

echo "✅ All prerequisites met"
exit 0
