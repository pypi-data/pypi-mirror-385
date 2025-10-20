#!/usr/bin/env bash
# Script: validate-spec.sh
# Purpose: Validate spec directory structure and task files exist
# Subsystem: backend
# Called by: /backend:develop, /backend:test slash commands
# Outputs: Exit 0 if valid, exit 1 if invalid

set -euo pipefail

# --- Configuration ---
SPEC_DIR="${1:-.}"
TASK_FILE="${2:-layered-tasks.md}"

# --- Main Logic ---
echo "[INFO] Validating spec directory: $SPEC_DIR"

# Check spec directory exists
if [ ! -d "$SPEC_DIR" ]; then
  echo "❌ Spec directory not found: $SPEC_DIR"
  exit 1
fi

# Check spec.md exists
if [ ! -f "$SPEC_DIR/spec.md" ]; then
  echo "❌ spec.md not found in: $SPEC_DIR"
  exit 1
fi

# Check for task file (layered-tasks.md or tasks.md)
TASK_PATH=""
if [ -f "$SPEC_DIR/agent-tasks/$TASK_FILE" ]; then
  TASK_PATH="$SPEC_DIR/agent-tasks/$TASK_FILE"
elif [ -f "$SPEC_DIR/agent-tasks/tasks.md" ]; then
  TASK_PATH="$SPEC_DIR/agent-tasks/tasks.md"
  echo "[INFO] Using tasks.md (simple project)"
else
  echo "❌ No task file found. Run /iterate:tasks $SPEC_DIR first"
  exit 1
fi

# --- Output ---
echo "✅ Spec validation passed"
echo "   Spec: $SPEC_DIR/spec.md"
echo "   Tasks: $TASK_PATH"
exit 0
