#!/bin/bash
# PURPOSE: Find frontend tasks from layered-tasks.md or tasks.md
# USAGE: ./find-frontend-tasks.sh <spec-directory> [role-filter]
# OUTPUT: JSON array of frontend tasks with status

set -euo pipefail

SPEC_DIR="${1:?Spec directory required}"
ROLE_FILTER="${2:-all}"

# Determine which task file to use
TASK_FILE=""
if [[ -f "$SPEC_DIR/agent-tasks/layered-tasks.md" ]]; then
    TASK_FILE="$SPEC_DIR/agent-tasks/layered-tasks.md"
elif [[ -f "$SPEC_DIR/tasks.md" ]]; then
    TASK_FILE="$SPEC_DIR/tasks.md"
else
    echo '{"error": "No task file found", "tasks": []}' | jq
    exit 1
fi

# Frontend-related keywords
FRONTEND_KEYWORDS="UI|Component|Page|Form|Layout|Routing|State|React|Next\.js|Vue|Angular|Svelte|Frontend|Client|Browser|CSS|Style|Design System|Tailwind|Material-UI|Chakra"

# Extract frontend tasks
TASKS=()
while IFS= read -r line; do
    # Match task lines: - [ ] T123 Description @agent
    if [[ "$line" =~ ^-[[:space:]]\[([x[:space:]])\][[:space:]]+(T[0-9]+)[[:space:]]+(.+)(@[a-z]+)? ]]; then
        STATUS="${BASH_REMATCH[1]}"
        TASK_ID="${BASH_REMATCH[2]}"
        DESCRIPTION="${BASH_REMATCH[3]}"
        AGENT="${BASH_REMATCH[4]:-@all}"

        # Check if task is frontend-related
        if [[ "$DESCRIPTION" =~ $FRONTEND_KEYWORDS ]]; then
            # Apply role filter if specified
            if [[ "$ROLE_FILTER" == "all" ]] || [[ "$AGENT" == "@$ROLE_FILTER" ]]; then
                COMPLETED="false"
                [[ "$STATUS" == "x" ]] && COMPLETED="true"

                TASKS+=("{\"id\": \"$TASK_ID\", \"description\": \"$DESCRIPTION\", \"agent\": \"$AGENT\", \"completed\": $COMPLETED}")
            fi
        fi
    fi
done < "$TASK_FILE"

# Output JSON array
echo "["
for i in "${!TASKS[@]}"; do
    echo "${TASKS[$i]}"
    if [[ $i -lt $((${#TASKS[@]} - 1)) ]]; then
        echo ","
    fi
done
echo "]" | jq
