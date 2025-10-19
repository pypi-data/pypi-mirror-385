#!/usr/bin/env bash
# Security Tool: Project File Discovery (Mechanics Only)
# Purpose: Find and list ALL project files for agent to analyze

set -euo pipefail

PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/env-analysis-context.txt}"

cd "$PROJECT_DIR" || exit 1

echo "[SCAN] Discovering project files..."
echo ""

# Just list everything - let the agent decide what's important
cat > "$OUTPUT_FILE" << EOF
# Project File Inventory
# Generated: $(date)
# Working Directory: $(pwd)

## All Specification Files
EOF

find specs -name "*.md" 2>/dev/null | sort >> "$OUTPUT_FILE" || echo "(none)" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

## All Documentation Files
EOF

find docs -name "*.md" 2>/dev/null | sort >> "$OUTPUT_FILE" || echo "(none)" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

## All Source Code
EOF

find src -type f 2>/dev/null | sort >> "$OUTPUT_FILE" || echo "(none)" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

## Configuration Files
EOF

# List common config files
for file in pyproject.toml package.json .mcp.json docker-compose.yml Dockerfile; do
  [[ -f "$file" ]] && echo "- $file" >> "$OUTPUT_FILE"
done

cat >> "$OUTPUT_FILE" << EOF

## Deployment Files
EOF

find deployment -type f 2>/dev/null | sort >> "$OUTPUT_FILE" || echo "(none)" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---
Agent: Analyze ALL files above to determine required environment variables.
EOF

# Show summary
TOTAL=$(cat "$OUTPUT_FILE" | grep -v "^#" | grep -v "^$" | grep -v "^---" | wc -l)
echo "✅ Listed $TOTAL files in: $OUTPUT_FILE"
echo ""

exit 0
