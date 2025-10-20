#!/usr/bin/env bash
# Script: worktree-list.sh
# Purpose: Lists all active worktrees with status
# Subsystem: git
# Called by: /git:worktree-create and /git:worktree-cleanup slash commands
# Outputs: JSON array of worktrees with metadata

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/worktree-list.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Listing git worktrees..."

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "[ERROR] Not a git repository"
    exit 1
fi

# Start JSON array
echo "{" > "$OUTPUT_FILE"
echo '  "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",' >> "$OUTPUT_FILE"
echo '  "repository": "'"$(basename "$(git rev-parse --show-toplevel)")"'",' >> "$OUTPUT_FILE"
echo '  "worktrees": [' >> "$OUTPUT_FILE"

# Get worktree list
WORKTREES=$(git worktree list --porcelain)

# Parse worktrees
FIRST=true
while IFS= read -r line; do
    if [[ $line =~ ^worktree\ (.+)$ ]]; then
        # Start new worktree entry
        if [ "$FIRST" = false ]; then
            echo "    }," >> "$OUTPUT_FILE"
        fi
        FIRST=false

        PATH="${BASH_REMATCH[1]}"
        echo "    {" >> "$OUTPUT_FILE"
        echo '      "path": "'"$PATH"'",' >> "$OUTPUT_FILE"
    elif [[ $line =~ ^HEAD\ ([a-f0-9]+)$ ]]; then
        COMMIT="${BASH_REMATCH[1]}"
        echo '      "head": "'"$COMMIT"'",' >> "$OUTPUT_FILE"
    elif [[ $line =~ ^branch\ (.+)$ ]]; then
        BRANCH="${BASH_REMATCH[1]}"
        echo '      "branch": "'"$BRANCH"'",' >> "$OUTPUT_FILE"
        echo '      "detached": false' >> "$OUTPUT_FILE"
    elif [[ $line =~ ^detached$ ]]; then
        echo '      "branch": null,' >> "$OUTPUT_FILE"
        echo '      "detached": true' >> "$OUTPUT_FILE"
    fi
done <<< "$WORKTREES"

# Close last entry if exists
if [ "$FIRST" = false ]; then
    echo "    }" >> "$OUTPUT_FILE"
fi

# Close JSON array and object
echo "  ]" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

# Count worktrees
COUNT=$(echo "$WORKTREES" | grep -c "^worktree " || true)

echo "[INFO] Found $COUNT worktree(s)"
echo "✅ Worktree list saved to: $OUTPUT_FILE"
exit 0
