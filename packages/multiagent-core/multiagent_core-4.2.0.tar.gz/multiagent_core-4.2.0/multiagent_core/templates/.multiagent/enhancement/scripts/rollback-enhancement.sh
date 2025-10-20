#!/bin/bash
# Rollback to pre-enhancement safety tag

set -e

# Get current branch to determine enhancement name
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [[ ! "$CURRENT_BRANCH" =~ ^enhancement/ ]]; then
    echo "❌ Error: Not on an enhancement branch"
    echo "Current branch: ${CURRENT_BRANCH}"
    echo ""
    echo "To rollback manually, find your tag:"
    echo "  git tag --list 'pre-enhancement/*'"
    echo "  git reset --hard <tag-name>"
    exit 1
fi

# Extract enhancement name from branch
ENHANCEMENT_NAME="${CURRENT_BRANCH#enhancement/}"

# Find matching tag
SAFETY_TAG=$(git tag --list "pre-enhancement/${ENHANCEMENT_NAME}-*" | head -1)

if [ -z "$SAFETY_TAG" ]; then
    echo "❌ Error: No safety tag found for enhancement: ${ENHANCEMENT_NAME}"
    echo ""
    echo "Available tags:"
    git tag --list "pre-enhancement/*"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  Enhancement Rollback"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Enhancement: ${ENHANCEMENT_NAME}"
echo "Current branch: ${CURRENT_BRANCH}"
echo "Safety tag: ${SAFETY_TAG}"
echo ""
echo "This will:"
echo "  - Reset to: ${SAFETY_TAG}"
echo "  - DISCARD all uncommitted changes"
echo "  - DISCARD all commits after the tag"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  WARNING: You have uncommitted changes:"
    git status --short
    echo ""
fi

read -p "Proceed with rollback? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Perform rollback
echo ""
echo "🔄 Resetting to ${SAFETY_TAG}..."
git reset --hard "${SAFETY_TAG}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Rollback Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Current state:"
git log -1 --oneline
echo ""
echo "Still on branch: ${CURRENT_BRANCH}"
echo ""
echo "To clean up enhancement:"
echo "  /enhancement:cleanup"
echo ""
echo "To switch back to main:"
echo "  git checkout main"
