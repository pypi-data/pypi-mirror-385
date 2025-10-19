#!/bin/bash
# Cleanup enhancement branch and tag

set -e

ENHANCEMENT_NAME="$1"

# If no name provided, try to detect from current branch
if [ -z "$ENHANCEMENT_NAME" ]; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [[ "$CURRENT_BRANCH" =~ ^enhancement/ ]]; then
        ENHANCEMENT_NAME="${CURRENT_BRANCH#enhancement/}"
    else
        echo "❌ Error: Enhancement name required"
        echo "Usage: /enhancement:cleanup <name>"
        echo ""
        echo "Or run from an enhancement branch"
        exit 1
    fi
fi

ENHANCEMENT_BRANCH="enhancement/${ENHANCEMENT_NAME}"
SAFETY_TAG=$(git tag --list "pre-enhancement/${ENHANCEMENT_NAME}-*" | head -1)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 Cleanup Enhancement"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Enhancement: ${ENHANCEMENT_NAME}"
echo ""

# Check if on enhancement branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
if [ "$CURRENT_BRANCH" = "$ENHANCEMENT_BRANCH" ]; then
    echo "⚠️  Currently on enhancement branch"
    echo "Switching to main first..."
    git checkout main
    echo ""
fi

# Delete branch
if git show-ref --verify --quiet "refs/heads/${ENHANCEMENT_BRANCH}"; then
    echo "🗑️  Deleting branch: ${ENHANCEMENT_BRANCH}"
    git branch -D "${ENHANCEMENT_BRANCH}"
    echo "✅ Branch deleted"
else
    echo "ℹ️  Branch not found: ${ENHANCEMENT_BRANCH}"
fi

# Delete tag
if [ -n "$SAFETY_TAG" ]; then
    echo "🗑️  Deleting tag: ${SAFETY_TAG}"
    git tag -d "${SAFETY_TAG}"
    echo "✅ Tag deleted"
else
    echo "ℹ️  No safety tag found for: ${ENHANCEMENT_NAME}"
fi

# Clean enhancement directory if exists
ENHANCEMENT_DIR="enhancements/${ENHANCEMENT_NAME}"
if [ -d "$ENHANCEMENT_DIR" ]; then
    echo "🗑️  Removing directory: ${ENHANCEMENT_DIR}/"
    rm -rf "$ENHANCEMENT_DIR"
    echo "✅ Directory removed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cleanup Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Enhancement '${ENHANCEMENT_NAME}' fully removed"
