#!/bin/bash
set -euo pipefail

# Check if proposal already exists in a spec
# Usage: find-proposal-in-spec.sh --type enhancement --filename core-redis-caching.md
# Output: Spec directory if found, empty if not found

TYPE=""
FILENAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TYPE="$2"
      shift 2
      ;;
    --filename)
      FILENAME="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Validate inputs
if [[ -z "$TYPE" ]] || [[ -z "$FILENAME" ]]; then
  echo "Usage: find-proposal-in-spec.sh --type enhancement --filename core-redis-caching.md" >&2
  exit 1
fi

# Pluralize type for directory name
if [[ "$TYPE" == "enhancement" ]]; then
  TYPE_PLURAL="enhancements"
elif [[ "$TYPE" == "refactor" ]]; then
  TYPE_PLURAL="refactors"
else
  echo "Invalid type: $TYPE" >&2
  exit 1
fi

# Search for proposal file in spec subdirectories
FOUND=$(find specs -type f -name "${TYPE}.md" -path "*/${TYPE_PLURAL}/*" -exec grep -l "$FILENAME" {} \; 2>/dev/null | head -1)

if [[ -n "$FOUND" ]]; then
  # Extract spec directory (go up 2 levels from the found file)
  dirname $(dirname "$FOUND")
fi
