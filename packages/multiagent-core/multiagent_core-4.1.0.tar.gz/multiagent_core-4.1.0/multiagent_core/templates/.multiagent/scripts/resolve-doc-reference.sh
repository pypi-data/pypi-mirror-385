#!/bin/bash
# PURPOSE: Resolve documentation reference aliases to actual file paths
# USAGE: resolve-doc-reference.sh <ALIAS|file_path>
# EXAMPLES:
#   resolve-doc-reference.sh ARCH_BUILD_STANDARDS
#   → docs/architecture/02-development-guide.md#coding-standards
#
#   resolve-doc-reference.sh ARCH_OVERVIEW
#   → docs/architecture/01-architecture-overview.md

set -euo pipefail

# Configuration file location
CONFIG_FILE="${MULTIAGENT_ROOT:-.}/.multiagent/docs-config.json"

# Check if config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: Config file not found: $CONFIG_FILE" >&2
    echo "Run this from a multiagent project root or set MULTIAGENT_ROOT" >&2
    exit 1
fi

# Get alias from argument
ALIAS="${1:-}"

if [[ -z "$ALIAS" ]]; then
    echo "USAGE: $0 <ALIAS>" >&2
    echo "Example: $0 ARCH_BUILD_STANDARDS" >&2
    exit 1
fi

# If it's already a file path, return as-is
if [[ "$ALIAS" == *".md"* ]] || [[ "$ALIAS" == docs/* ]]; then
    echo "$ALIAS"
    exit 0
fi

# Search for alias in config file
# Try architecture section
RESULT=$(jq -r --arg alias "$ALIAS" '
  .architecture[] | select(.alias == $alias) |
  .file + (if .section then "#" + .section else "" end)
' "$CONFIG_FILE" 2>/dev/null | head -1)

# If not found, try sections
if [[ -z "$RESULT" ]]; then
    RESULT=$(jq -r --arg alias "$ALIAS" '
      .sections[] | select(.alias == $alias) |
      .file + (if .section then "#" + .section else "" end)
    ' "$CONFIG_FILE" 2>/dev/null | head -1)
fi

# If not found, try guides
if [[ -z "$RESULT" ]]; then
    RESULT=$(jq -r --arg alias "$ALIAS" '
      .guides[] | select(.alias == $alias) |
      .file + (if .section then "#" + .section else "" end)
    ' "$CONFIG_FILE" 2>/dev/null | head -1)
fi

# Output result or error
if [[ -n "$RESULT" ]] && [[ "$RESULT" != "null" ]]; then
    echo "$RESULT"
    exit 0
else
    echo "ERROR: Alias '$ALIAS' not found in $CONFIG_FILE" >&2
    echo "Available aliases:" >&2
    jq -r '.architecture[].alias, .sections[].alias, .guides[].alias' "$CONFIG_FILE" | sort >&2
    exit 1
fi
