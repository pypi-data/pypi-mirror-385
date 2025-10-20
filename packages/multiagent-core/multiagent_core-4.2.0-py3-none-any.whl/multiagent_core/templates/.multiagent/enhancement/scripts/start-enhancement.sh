#!/bin/bash
# Start a new enhancement with safety tag and tracking

set -e

ENHANCEMENT_NAME="$1"

if [ -z "$ENHANCEMENT_NAME" ]; then
    echo "❌ Error: Enhancement name required"
    echo "Usage: /enhancement:start <name>"
    exit 1
fi

# Validate we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Commit or stash your changes first."
        exit 1
    fi
fi

# Get current state
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFETY_TAG="pre-enhancement/${ENHANCEMENT_NAME}-${TIMESTAMP}"
ENHANCEMENT_BRANCH="enhancement/${ENHANCEMENT_NAME}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Starting Enhancement: ${ENHANCEMENT_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Create safety tag on current commit
echo "📍 Creating safety tag: ${SAFETY_TAG}"
git tag -a "${SAFETY_TAG}" -m "Safety snapshot before enhancement: ${ENHANCEMENT_NAME}"
echo "✅ Safety tag created at ${CURRENT_COMMIT}"
echo ""

# 2. Create and checkout enhancement branch
echo "🌿 Creating enhancement branch: ${ENHANCEMENT_BRANCH}"
git checkout -b "${ENHANCEMENT_BRANCH}"
echo "✅ Switched to ${ENHANCEMENT_BRANCH}"
echo ""

# 3. Create enhancement directory
ENHANCEMENT_DIR="enhancements/${ENHANCEMENT_NAME}"
mkdir -p "${ENHANCEMENT_DIR}"
echo "📁 Created: ${ENHANCEMENT_DIR}/"
echo ""

# 4. Generate ENHANCEMENT_LOG.md from template
TEMPLATE_PATH="$HOME/.multiagent/enhancement/templates/ENHANCEMENT_LOG.md"
LOG_PATH="${ENHANCEMENT_DIR}/ENHANCEMENT_LOG.md"

if [ -f "${TEMPLATE_PATH}" ]; then
    # Replace placeholders
    sed -e "s/{{ENHANCEMENT_NAME}}/${ENHANCEMENT_NAME}/g" \
        -e "s/{{DATE}}/$(date +%Y-%m-%d)/g" \
        -e "s/{{SAFETY_TAG}}/${SAFETY_TAG}/g" \
        -e "s/{{CURRENT_BRANCH}}/${CURRENT_BRANCH}/g" \
        -e "s/{{CURRENT_COMMIT}}/${CURRENT_COMMIT}/g" \
        -e "s/{{HAS_UNCOMMITTED}}/$(if git diff-index --quiet HEAD --; then echo 'No'; else echo 'Yes'; fi)/g" \
        -e "s/{{HYPOTHESIS}}/[Document your hypothesis here]/g" \
        -e "s/{{LEARNINGS}}/[Will document as you progress]/g" \
        -e "s/{{NEXT_STEPS}}/[Will determine based on results]/g" \
        "${TEMPLATE_PATH}" > "${LOG_PATH}"

    echo "📝 Created: ${LOG_PATH}"
else
    echo "⚠️  Warning: Template not found, creating basic log"
    cat > "${LOG_PATH}" <<EOF
# Enhancement: ${ENHANCEMENT_NAME}

**Started:** $(date +%Y-%m-%d)
**Branch:** ${ENHANCEMENT_BRANCH}
**Safety Tag:** ${SAFETY_TAG}

## Progress

Document your enhancement progress here.
EOF
fi

# 5. Create initial commit
git add "${ENHANCEMENT_DIR}/"
git commit -m "[ENHANCEMENT] Start: ${ENHANCEMENT_NAME}

Safety tag: ${SAFETY_TAG}
Branched from: ${CURRENT_BRANCH} @ ${CURRENT_COMMIT}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Enhancement Started Successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Rollback point: ${SAFETY_TAG}"
echo "🌿 Working branch: ${ENHANCEMENT_BRANCH}"
echo "📝 Enhancement log: ${LOG_PATH}"
echo ""
echo "Next steps:"
echo "  1. Edit ${LOG_PATH} with your hypothesis"
echo "  2. Make changes and commit to this branch"
echo "  3. When done: /enhancement:archive or /enhancement:integrate"
echo "  4. If needed: /enhancement:rollback"
echo ""
echo "🔒 Safe to enhancement - you can always rollback!"
