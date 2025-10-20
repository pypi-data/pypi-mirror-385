#!/usr/bin/env bash
# Script: find-backend-tasks.sh
# Purpose: Extract backend tasks from layered-tasks.md or tasks.md filtered by role
# Subsystem: backend
# Called by: /backend:develop slash command
# Outputs: List of backend tasks to stdout

set -euo pipefail

# --- Configuration ---
SPEC_DIR="${1:-.}"
ROLE="${2:-all}"

# --- Main Logic ---
echo "[INFO] Finding backend tasks in $SPEC_DIR (Role: $ROLE)"

# Determine task file
TASK_FILE=""
if [ -f "$SPEC_DIR/agent-tasks/layered-tasks.md" ]; then
  TASK_FILE="$SPEC_DIR/agent-tasks/layered-tasks.md"
elif [ -f "$SPEC_DIR/agent-tasks/tasks.md" ]; then
  TASK_FILE="$SPEC_DIR/agent-tasks/tasks.md"
else
  echo "❌ No task file found"
  exit 1
fi

# Backend domain keywords
KEYWORDS="Backend|API|Endpoint|Database|Model|Service|Auth|Server|Migration|Schema"
KEYWORDS="$KEYWORDS|Express|FastAPI|Django|Prisma|PostgreSQL|MongoDB|REST|GraphQL"

# Find backend tasks
if [ "$ROLE" = "all" ]; then
  # All backend tasks
  grep -iE "($KEYWORDS)" "$TASK_FILE" || echo "No backend tasks found"
else
  # Filter by role (@claude, @copilot, etc.)
  grep -iE "($KEYWORDS)" "$TASK_FILE" | grep "@$ROLE" || echo "No backend tasks found for @$ROLE"
fi

# --- Output ---
exit 0
