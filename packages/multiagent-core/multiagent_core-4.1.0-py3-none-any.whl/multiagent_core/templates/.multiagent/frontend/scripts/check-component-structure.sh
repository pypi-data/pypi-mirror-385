#!/bin/bash
# PURPOSE: Check frontend component structure and organization
# USAGE: ./check-component-structure.sh [src-directory]
# OUTPUT: JSON with component analysis

set -euo pipefail

SRC_DIR="${1:-src}"

if [[ ! -d "$SRC_DIR" ]]; then
    echo '{"error": "Source directory not found: '"$SRC_DIR"'", "components": 0}' | jq
    exit 1
fi

# Count components by type
COMPONENT_COUNT=$(find "$SRC_DIR" -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" -o -name "*.svelte" | wc -l)
PAGE_COUNT=$(find "$SRC_DIR" -path "*/pages/*" -o -path "*/app/*" -o -path "*/routes/*" | grep -E "\.(tsx|jsx|vue|svelte)$" | wc -l || echo 0)
LAYOUT_COUNT=$(find "$SRC_DIR" -name "*layout*" -o -name "*Layout*" | grep -E "\.(tsx|jsx|vue|svelte)$" | wc -l || echo 0)
FORM_COUNT=$(find "$SRC_DIR" -name "*form*" -o -name "*Form*" | grep -E "\.(tsx|jsx|vue|svelte)$" | wc -l || echo 0)

# Check for common directories
HAS_COMPONENTS=false
HAS_PAGES=false
HAS_LAYOUTS=false
HAS_UTILS=false
HAS_HOOKS=false
HAS_STYLES=false

[[ -d "$SRC_DIR/components" ]] && HAS_COMPONENTS=true
[[ -d "$SRC_DIR/pages" ]] || [[ -d "$SRC_DIR/app" ]] && HAS_PAGES=true
[[ -d "$SRC_DIR/layouts" ]] && HAS_LAYOUTS=true
[[ -d "$SRC_DIR/utils" ]] || [[ -d "$SRC_DIR/lib" ]] && HAS_UTILS=true
[[ -d "$SRC_DIR/hooks" ]] && HAS_HOOKS=true
[[ -d "$SRC_DIR/styles" ]] || [[ -d "$SRC_DIR/css" ]] && HAS_STYLES=true

# Output JSON
cat <<EOF
{
  "sourceDirectory": "$SRC_DIR",
  "componentCount": $COMPONENT_COUNT,
  "pageCount": $PAGE_COUNT,
  "layoutCount": $LAYOUT_COUNT,
  "formCount": $FORM_COUNT,
  "structure": {
    "components": $HAS_COMPONENTS,
    "pages": $HAS_PAGES,
    "layouts": $HAS_LAYOUTS,
    "utils": $HAS_UTILS,
    "hooks": $HAS_HOOKS,
    "styles": $HAS_STYLES
  }
}
EOF
