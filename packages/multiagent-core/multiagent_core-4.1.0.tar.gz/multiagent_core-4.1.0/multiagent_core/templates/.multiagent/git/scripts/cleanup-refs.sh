#!/usr/bin/env bash
# Script: cleanup-refs.sh
# Purpose: Removes stale git references
# Subsystem: git
# Called by: /git:worktree-cleanup and /git:branch-cleanup slash commands
# Outputs: List of cleaned references

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/cleanup-refs.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Cleaning up stale git references..."

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "[ERROR] Not a git repository"
    exit 1
fi

# Start JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "$(basename "$(git rev-parse --show-toplevel)")",
  "cleaned": []
}
EOF

# Prune worktree references
echo "[INFO] Pruning worktree references..."
WORKTREE_PRUNE_OUTPUT=$(git worktree prune --verbose 2>&1 || true)

# Prune remote tracking branches
echo "[INFO] Pruning remote tracking branches..."
FETCH_PRUNE_OUTPUT=$(git fetch --all --prune 2>&1 || true)

# Remove stale remote branches that no longer exist
echo "[INFO] Checking for stale remote refs..."
STALE_REFS=()
while IFS= read -r ref; do
    if [[ -n "$ref" ]]; then
        STALE_REFS+=("$ref")
    fi
done < <(git for-each-ref --format='%(refname)' refs/remotes/ | while read -r ref; do
    # Check if remote branch still exists
    BRANCH_NAME=${ref#refs/remotes/origin/}
    if ! git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
        echo "$ref"
    fi
done)

# Delete stale remote refs
for ref in "${STALE_REFS[@]}"; do
    echo "[INFO] Removing stale ref: $ref"
    git update-ref -d "$ref" 2>/dev/null || true
done

# Run git gc to cleanup
echo "[INFO] Running git garbage collection..."
git gc --auto --quiet 2>&1 || true

# Update JSON output with cleaned refs
if [ ${#STALE_REFS[@]} -gt 0 ]; then
    REFS_JSON=$(printf ',"%s"' "${STALE_REFS[@]}")
    REFS_JSON="[${REFS_JSON:1}]"
else
    REFS_JSON="[]"
fi

cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "$(basename "$(git rev-parse --show-toplevel)")",
  "cleaned": $REFS_JSON,
  "worktree_prune": "$(echo "$WORKTREE_PRUNE_OUTPUT" | head -1 || echo 'No stale worktrees')",
  "fetch_prune": "Pruned remote tracking branches",
  "gc_run": true
}
EOF

# Count cleaned refs
COUNT=${#STALE_REFS[@]}

echo "[INFO] Cleaned $COUNT stale reference(s)"
echo "✅ Cleanup report saved to: $OUTPUT_FILE"
exit 0
