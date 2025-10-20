#!/bin/bash
# Framework-specific doc drift detection for multiagent-core development
# Called by post-commit hook to detect when framework docs need updating

# Get the last commit changes
CHANGED_FILES=$(git diff HEAD~1 --name-only 2>/dev/null)

# Track if any drift detected
DRIFT_DETECTED=0

echo "🔍 Checking framework documentation drift..."

# Check if framework core changed
if echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/"; then
    echo "⚠️  Framework templates changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md"
    DRIFT_DETECTED=1
fi

# Check if CLI changed
if echo "$CHANGED_FILES" | grep -q "multiagent_core/cli.py"; then
    echo "⚠️  CLI commands changed"
    echo "   → Consider updating: README.md (Core Commands section)"
    echo "   → Consider updating: docs/architecture/03-build-system.md"
    DRIFT_DETECTED=1
fi

# Check if architecture docs changed but overview wasn't updated
if echo "$CHANGED_FILES" | grep -q "docs/architecture/" && ! echo "$CHANGED_FILES" | grep -q "docs/architecture/01-overview.md"; then
    echo "⚠️  Architecture docs changed"
    echo "   → Consider updating: docs/architecture/01-overview.md"
    DRIFT_DETECTED=1
fi

# Check if new subsystem added
if echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/[^/]*/README.md"; then
    echo "⚠️  Subsystem README changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md (Subsystem Overview)"
    DRIFT_DETECTED=1
fi

# Check if slash command templates added
if echo "$CHANGED_FILES" | grep -q ".claude/commands/" && ! echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/README.md"; then
    echo "⚠️  Slash commands changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md"
    DRIFT_DETECTED=1
fi

if [ $DRIFT_DETECTED -eq 1 ]; then
    # Create queue directory if it doesn't exist
    QUEUE_DIR="$HOME/.multiagent/documentation/queue"
    mkdir -p "$QUEUE_DIR"

    # Create timestamped queue entry
    TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
    QUEUE_FILE="$QUEUE_DIR/update-request-$TIMESTAMP.json"

    # Write queue entry with structured data
    cat > "$QUEUE_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "commit_hash": "$(git rev-parse HEAD)",
  "commit_message": "$(git log -1 --pretty=%B | head -1)",
  "changed_files": $(echo "$CHANGED_FILES" | jq -R . | jq -s .),
  "update_type": "framework",
  "recommendations": [
    "Run /docs:update --check-patterns to review and update documentation",
    "Verify multiagent_core/templates/.multiagent/README.md reflects changes",
    "Check docs/architecture/ for consistency"
  ]
}
EOF

    echo "📋 Documentation update request queued: $QUEUE_FILE"
    echo ""
    echo "📝 To process queued updates:"
    echo "   /docs:auto-update              # Process all queued updates"
    echo "   /docs:update-check             # Manual review and update"
    echo ""
else
    echo "✓ No documentation drift detected"
fi

exit 0
