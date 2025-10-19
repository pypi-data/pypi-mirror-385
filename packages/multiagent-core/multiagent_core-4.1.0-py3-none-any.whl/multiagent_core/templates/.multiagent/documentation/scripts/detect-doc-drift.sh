#!/bin/bash
# Generic doc drift detection for user projects
# Deployed to projects via multiagent init
# Configured by /core:project-setup based on project type

# Get last commit changes
CHANGED_FILES=$(git diff HEAD~1 --name-only 2>/dev/null)
DRIFT_DETECTED=0

echo "🔍 Checking documentation drift..."

# Project type detection (replaced during /core:project-setup)
PROJECT_TYPE="{{PROJECT_TYPE}}"  # landing-page | website | web-app | ai-app | saas

# Universal checks (all project types)

# 1. Source code changes
if echo "$CHANGED_FILES" | grep -qE "^(src/|app/|lib/|components/|pages/|views/)"; then
    echo "⚠️  Source code changed"
    echo "   → Consider updating: README.md, docs/architecture/"
    DRIFT_DETECTED=1
fi

# 2. Configuration changes
if echo "$CHANGED_FILES" | grep -qE "^(\.env\.example|config/|\.multiagent/config\.json)"; then
    echo "⚠️  Configuration changed"
    echo "   → Consider updating: README.md (Setup section)"
    DRIFT_DETECTED=1
fi

# 3. Dependencies changed
if echo "$CHANGED_FILES" | grep -qE "^(package\.json|pyproject\.toml|requirements\.txt|Cargo\.toml)"; then
    echo "⚠️  Dependencies changed"
    echo "   → Consider updating: README.md (Installation)"
    DRIFT_DETECTED=1
fi

# Type-specific checks

# Backend changes (web-app, ai-app, saas only)
if [[ "$PROJECT_TYPE" =~ ^(web-app|ai-app|saas)$ ]]; then
    if echo "$CHANGED_FILES" | grep -qE "^(api/|server/|backend/|routes/)"; then
        echo "⚠️  Backend code changed"
        echo "   → Consider updating: docs/API.md"
        DRIFT_DETECTED=1
    fi

    # Database changes
    if echo "$CHANGED_FILES" | grep -qE "^(schema|migrations|models|database)/"; then
        echo "⚠️  Database schema changed"
        echo "   → Consider updating: docs/architecture/database.md"
        DRIFT_DETECTED=1
    fi
fi

# AI-specific changes (ai-app, saas only)
if [[ "$PROJECT_TYPE" =~ ^(ai-app|saas)$ ]]; then
    if echo "$CHANGED_FILES" | grep -qE "^(ai/|ml/|models/|prompts/)"; then
        echo "⚠️  AI/ML code changed"
        echo "   → Consider updating: docs/AI.md"
        DRIFT_DETECTED=1
    fi
fi

# Docs changed but README not updated
if echo "$CHANGED_FILES" | grep -q "^docs/" && ! echo "$CHANGED_FILES" | grep -q "README.md"; then
    echo "⚠️  Documentation changed"
    echo "   → Consider updating: README.md (to link new docs)"
    DRIFT_DETECTED=1
fi

if [ $DRIFT_DETECTED -eq 1 ]; then
    # Create queue directory if it doesn't exist
    QUEUE_DIR=".multiagent/documentation/queue"
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
  "project_type": "$PROJECT_TYPE",
  "update_type": "project",
  "recommendations": [
    "Run /docs:auto-update to process queued documentation updates",
    "Review README.md and docs/architecture/overview.md for accuracy",
    "Update code examples if API changed"
  ]
}
EOF

    echo "📋 Documentation update request queued: $QUEUE_FILE"
    echo ""
    echo "📝 To process queued updates:"
    echo "   /docs:auto-update              # Process all queued updates automatically"
    echo "   /docs:update-check             # Manual review and update"
    echo ""
else
    echo "✓ No documentation drift detected"
fi

exit 0
