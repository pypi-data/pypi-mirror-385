#!/usr/bin/env bash
# Script: list-enhancements.sh
# Purpose: List all enhancements with status in formatted table
# Subsystem: enhancement
# Called by: /enhancement:list slash command
# Outputs: Formatted list grouped by status

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
FILTER_STATUS="${2:-}"
FILTER_PRIORITY="${3:-}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

# Check if enhancements directory exists
if [[ ! -d "enhancements" || -z "$(ls -A enhancements 2>/dev/null)" ]]; then
    echo "📋 No enhancements found"
    echo ""
    echo "Create enhancements:"
    echo "  /enhancement:create \"Enhancement title\""
    echo "  /github:pr-review {pr-number}"
    exit 0
fi

# Status groups
declare -A STATUS_GROUPS
STATUS_GROUPS["not-started"]="🔴 Not Started"
STATUS_GROUPS["analyzed"]="✅ Analyzed - Ready for Review"
STATUS_GROUPS["ready"]="🟢 Ready to Implement"
STATUS_GROUPS["in-progress"]="🔵 In Progress"
STATUS_GROUPS["blocked"]="⚠️  Blocked"
STATUS_GROUPS["completed"]="✅ Completed"
STATUS_GROUPS["deferred"]="🟡 Deferred"
STATUS_GROUPS["rejected"]="❌ Rejected"

# Arrays to hold enhancements by status
declare -A ENHANCEMENTS
for status in "${!STATUS_GROUPS[@]}"; do
    ENHANCEMENTS["$status"]=""
done

TOTAL=0

# Read all enhancement status files
for dir in enhancements/*/; do
    if [[ ! -f "${dir}status.json" ]]; then
        continue
    fi

    ID=$(jq -r '.id' "${dir}status.json" 2>/dev/null || echo "???")
    TITLE=$(jq -r '.title' "${dir}status.json" 2>/dev/null || echo "Unknown")
    STATUS=$(jq -r '.status' "${dir}status.json" 2>/dev/null || echo "not-started")
    PRIORITY=$(jq -r '.priority' "${dir}status.json" 2>/dev/null || echo "medium")
    CREATED=$(jq -r '.created' "${dir}status.json" 2>/dev/null | cut -d'T' -f1 || echo "")
    SCORE=$(jq -r '.analysis.priority_score // "-"' "${dir}status.json" 2>/dev/null || echo "-")

    # Apply filters if specified
    if [[ -n "$FILTER_STATUS" && "$STATUS" != "$FILTER_STATUS" ]]; then
        continue
    fi

    if [[ -n "$FILTER_PRIORITY" && "$PRIORITY" != "$FILTER_PRIORITY" ]]; then
        continue
    fi

    # Format entry
    ENTRY=$(printf "  %-4s %-40s %-8s %-6s %-10s\n" "$ID" "$TITLE" "$PRIORITY" "$SCORE" "$CREATED")

    ENHANCEMENTS["$STATUS"]+="$ENTRY"$'\n'
    ((TOTAL++))
done

# Display header
echo "📋 Enhancement List (Total: $TOTAL)"
echo ""

# Display each status group
for status in not-started analyzed ready in-progress blocked completed deferred rejected; do
    if [[ -n "${ENHANCEMENTS[$status]}" ]]; then
        COUNT=$(echo "${ENHANCEMENTS[$status]}" | grep -c "^  " || echo "0")
        echo "${STATUS_GROUPS[$status]} ($COUNT):"
        echo "  ID   Title                                    Priority Score  Created"
        echo "${ENHANCEMENTS[$status]}"
    fi
done

# Summary
echo "---"
echo "Summary: $TOTAL total enhancements"
echo ""

# Suggest next actions
ANALYZED_COUNT=$(echo "${ENHANCEMENTS[analyzed]}" | grep -c "^  " || echo "0")
READY_COUNT=$(echo "${ENHANCEMENTS[ready]}" | grep -c "^  " || echo "0")
NOT_STARTED_COUNT=$(echo "${ENHANCEMENTS[not-started]}" | grep -c "^  " || echo "0")

if [[ $ANALYZED_COUNT -gt 0 ]]; then
    echo "💡 $ANALYZED_COUNT need review: /enhancement:status {ID} ready"
fi

if [[ $READY_COUNT -gt 0 ]]; then
    echo "💡 $READY_COUNT ready to start: /enhancement:start {ID}"
fi

if [[ $NOT_STARTED_COUNT -gt 0 ]]; then
    echo "💡 $NOT_STARTED_COUNT need analysis: /enhancement:analyze --all"
fi

exit 0
