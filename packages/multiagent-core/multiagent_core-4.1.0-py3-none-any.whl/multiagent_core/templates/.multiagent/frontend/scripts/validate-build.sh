#!/bin/bash
# PURPOSE: Validate frontend build output exists and is complete
# USAGE: ./validate-build.sh [build-directory]
# OUTPUT: JSON with validation results

set -euo pipefail

BUILD_DIR="${1:-}"

# Auto-detect build directory if not provided
if [[ -z "$BUILD_DIR" ]]; then
    if [[ -d ".next" ]]; then
        BUILD_DIR=".next"
    elif [[ -d "build" ]]; then
        BUILD_DIR="build"
    elif [[ -d "dist" ]]; then
        BUILD_DIR="dist"
    else
        echo '{"valid": false, "error": "No build directory found"}' | jq
        exit 1
    fi
fi

# Check if build directory exists
if [[ ! -d "$BUILD_DIR" ]]; then
    echo '{"valid": false, "error": "Build directory does not exist: '"$BUILD_DIR"'"}' | jq
    exit 1
fi

# Count files in build directory
FILE_COUNT=$(find "$BUILD_DIR" -type f | wc -l)

# Check for essential build artifacts
HAS_HTML=false
HAS_JS=false
HAS_CSS=false

if find "$BUILD_DIR" -name "*.html" -type f | grep -q .; then
    HAS_HTML=true
fi

if find "$BUILD_DIR" -name "*.js" -type f | grep -q .; then
    HAS_JS=true
fi

if find "$BUILD_DIR" -name "*.css" -type f | grep -q .; then
    HAS_CSS=true
fi

# Calculate total build size
BUILD_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)

# Determine if build is valid (at least has JS files)
VALID=false
if [[ "$FILE_COUNT" -gt 0 ]] && [[ "$HAS_JS" == "true" ]]; then
    VALID=true
fi

# Output JSON
cat <<EOF
{
  "valid": $VALID,
  "buildDirectory": "$BUILD_DIR",
  "fileCount": $FILE_COUNT,
  "buildSize": "$BUILD_SIZE",
  "artifacts": {
    "html": $HAS_HTML,
    "javascript": $HAS_JS,
    "css": $HAS_CSS
  }
}
EOF
