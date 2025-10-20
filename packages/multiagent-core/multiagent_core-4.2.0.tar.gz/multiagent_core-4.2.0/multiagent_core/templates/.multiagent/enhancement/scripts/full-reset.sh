#!/bin/bash
# Full reset: rollback + cleanup in one command

set -e

ENHANCEMENT_NAME="$1"

if [ -z "$ENHANCEMENT_NAME" ]; then
    # Try to detect from current branch
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [[ "$CURRENT_BRANCH" =~ ^enhancement/ ]]; then
        ENHANCEMENT_NAME="${CURRENT_BRANCH#enhancement/}"
    else
        echo "❌ Error: Enhancement name required or run from enhancement branch"
        echo "Usage: /enhancement:full-reset <name>"
        exit 1
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Full Enhancement Reset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Rollback to safety tag"
echo "  2. Cleanup branch and tag"
echo "  3. Return to main branch"
echo ""
echo "Enhancement: ${ENHANCEMENT_NAME}"
echo ""

read -p "Proceed with full reset? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1/3: Rolling back..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run rollback (suppress interactive prompt)
SAFETY_TAG=$(git tag --list "pre-enhancement/${ENHANCEMENT_NAME}-*" | head -1)
if [ -n "$SAFETY_TAG" ]; then
    git reset --hard "${SAFETY_TAG}"
    echo "✅ Rolled back to ${SAFETY_TAG}"
else
    echo "⚠️  No safety tag found, skipping rollback"
fi

echo ""
echo "Step 2/3: Switching to main..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git checkout main
echo "✅ On main branch"

echo ""
echo "Step 3/3: Cleaning up..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Delete branch
ENHANCEMENT_BRANCH="enhancement/${ENHANCEMENT_NAME}"
if git show-ref --verify --quiet "refs/heads/${ENHANCEMENT_BRANCH}"; then
    git branch -D "${ENHANCEMENT_BRANCH}"
    echo "✅ Deleted branch: ${ENHANCEMENT_BRANCH}"
fi

# Delete tag
if [ -n "$SAFETY_TAG" ]; then
    git tag -d "${SAFETY_TAG}"
    echo "✅ Deleted tag: ${SAFETY_TAG}"
fi

# Delete directory
ENHANCEMENT_DIR="enhancements/${ENHANCEMENT_NAME}"
if [ -d "$ENHANCEMENT_DIR" ]; then
    rm -rf "$ENHANCEMENT_DIR"
    echo "✅ Deleted directory: ${ENHANCEMENT_DIR}/"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Full Reset Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You're back on main with clean state"
echo "Enhancement '${ENHANCEMENT_NAME}' fully removed"
