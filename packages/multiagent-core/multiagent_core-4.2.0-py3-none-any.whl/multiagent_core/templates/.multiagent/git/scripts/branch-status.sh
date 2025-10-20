#!/usr/bin/env bash
# Script: branch-status.sh
# Purpose: Checks branch merge status and activity
# Subsystem: git
# Called by: /git:branch-cleanup slash command
# Outputs: JSON status of branch merge state and activity

set -euo pipefail

# --- Configuration ---
BRANCH_NAME="${1:-.}"
BASE_BRANCH="${2:-main}"
OUTPUT_FILE="${3:-/tmp/branch-status.json}"

# --- Main Logic ---

echo "[INFO] Analyzing branch: $BRANCH_NAME..."

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "[ERROR] Not a git repository"
    exit 1
fi

# Check if branch exists
if ! git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
    echo "[ERROR] Branch '$BRANCH_NAME' does not exist"
    exit 1
fi

# Check if base branch exists
if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
    echo "[WARN] Base branch '$BASE_BRANCH' not found, trying 'master'..."
    BASE_BRANCH="master"
    if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
        echo "[ERROR] Neither 'main' nor 'master' branch found"
        exit 1
    fi
fi

# Check if branch is merged
MERGED=false
if git branch --merged "$BASE_BRANCH" | grep -q "^[* ]*$BRANCH_NAME$"; then
    MERGED=true
fi

# Get ahead/behind counts
AHEAD_BEHIND=$(git rev-list --left-right --count "$BASE_BRANCH...$BRANCH_NAME" 2>/dev/null || echo "0	0")
AHEAD=$(echo "$AHEAD_BEHIND" | awk '{print $2}')
BEHIND=$(echo "$AHEAD_BEHIND" | awk '{print $1}')

# Get last commit info
LAST_COMMIT_HASH=$(git rev-parse "$BRANCH_NAME")
LAST_COMMIT_DATE=$(git log -1 --format='%cI' "$BRANCH_NAME")
LAST_COMMIT_MSG=$(git log -1 --format='%s' "$BRANCH_NAME")

# Calculate days since last commit
LAST_COMMIT_UNIX=$(date -d "$LAST_COMMIT_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$LAST_COMMIT_DATE" +%s 2>/dev/null || echo "0")
NOW_UNIX=$(date +%s)
DAYS_OLD=$(( (NOW_UNIX - LAST_COMMIT_UNIX) / 86400 ))

# Check if branch has upstream
UPSTREAM=$(git rev-parse --abbrev-ref "$BRANCH_NAME@{upstream}" 2>/dev/null || echo "none")

# Generate JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "branch": "$BRANCH_NAME",
  "base_branch": "$BASE_BRANCH",
  "merged": $MERGED,
  "upstream": "$UPSTREAM",
  "ahead": $AHEAD,
  "behind": $BEHIND,
  "last_commit": {
    "hash": "$LAST_COMMIT_HASH",
    "date": "$LAST_COMMIT_DATE",
    "message": "$LAST_COMMIT_MSG",
    "days_old": $DAYS_OLD
  },
  "stale": $([ $DAYS_OLD -gt 30 ] && echo "true" || echo "false"),
  "safe_to_delete": $([ "$MERGED" = "true" ] && echo "true" || echo "false")
}
EOF

echo "[INFO] Branch is $([ "$MERGED" = "true" ] && echo "MERGED" || echo "NOT MERGED")"
echo "[INFO] Last activity: $DAYS_OLD days ago"
echo "✅ Branch status saved to: $OUTPUT_FILE"
exit 0
