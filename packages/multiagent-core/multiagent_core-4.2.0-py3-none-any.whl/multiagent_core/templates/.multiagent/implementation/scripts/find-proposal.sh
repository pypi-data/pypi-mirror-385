#!/bin/bash
set -euo pipefail

# Find proposal file by type and ID
# Usage: find-proposal.sh --type enhancement --id 001
# Output: Full path to proposal file or empty if not found

TYPE=""
ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TYPE="$2"
      shift 2
      ;;
    --id)
      ID="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Validate inputs
if [[ -z "$TYPE" ]] || [[ -z "$ID" ]]; then
  echo "Usage: find-proposal.sh --type enhancement --id 001" >&2
  exit 1
fi

# Search for proposal file
if [[ "$TYPE" == "enhancement" ]]; then
  find docs/enhancements -type f -name "*${ID}*.md" ! -name "*-ANALYSIS.md" | head -1
elif [[ "$TYPE" == "refactor" ]]; then
  find docs/refactors -type f -name "*${ID}*.md" ! -name "*-ANALYSIS.md" | head -1
elif [[ "$TYPE" == "idea" ]]; then
  if [[ -f "docs/ideas/${ID}.md" ]]; then
    echo "docs/ideas/${ID}.md"
  fi
else
  echo "Invalid type: $TYPE" >&2
  exit 1
fi
