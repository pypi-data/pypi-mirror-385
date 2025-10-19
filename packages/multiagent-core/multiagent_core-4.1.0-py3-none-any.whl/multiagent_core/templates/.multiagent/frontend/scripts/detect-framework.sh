#!/bin/bash
# PURPOSE: Detect frontend framework from package.json and output configuration
# USAGE: ./detect-framework.sh [path-to-package.json]
# OUTPUT: JSON with framework, version, build command, dev command

set -euo pipefail

PACKAGE_JSON="${1:-package.json}"

if [[ ! -f "$PACKAGE_JSON" ]]; then
    echo '{"error": "package.json not found", "framework": "unknown"}' | jq
    exit 1
fi

# Extract framework information
FRAMEWORK="unknown"
VERSION=""
BUILD_CMD="npm run build"
DEV_CMD="npm run dev"
TEST_CMD="npm test"

# Check for Next.js
if jq -e '.dependencies["next"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    FRAMEWORK="next.js"
    VERSION=$(jq -r '.dependencies["next"]' "$PACKAGE_JSON")
    BUILD_CMD="npm run build"
    DEV_CMD="npm run dev"

# Check for React (Create React App or Vite)
elif jq -e '.dependencies["react"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    if jq -e '.dependencies["vite"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
        FRAMEWORK="react-vite"
        VERSION=$(jq -r '.dependencies["react"]' "$PACKAGE_JSON")
        BUILD_CMD="npm run build"
        DEV_CMD="npm run dev"
    else
        FRAMEWORK="react"
        VERSION=$(jq -r '.dependencies["react"]' "$PACKAGE_JSON")
        BUILD_CMD="npm run build"
        DEV_CMD="npm start"
    fi

# Check for Vue
elif jq -e '.dependencies["vue"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    FRAMEWORK="vue"
    VERSION=$(jq -r '.dependencies["vue"]' "$PACKAGE_JSON")
    BUILD_CMD="npm run build"
    DEV_CMD="npm run dev"

# Check for Angular
elif jq -e '.dependencies["@angular/core"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    FRAMEWORK="angular"
    VERSION=$(jq -r '.dependencies["@angular/core"]' "$PACKAGE_JSON")
    BUILD_CMD="npm run build"
    DEV_CMD="npm start"

# Check for Svelte
elif jq -e '.dependencies["svelte"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    FRAMEWORK="svelte"
    VERSION=$(jq -r '.dependencies["svelte"]' "$PACKAGE_JSON")
    BUILD_CMD="npm run build"
    DEV_CMD="npm run dev"
fi

# Check for TypeScript
HAS_TYPESCRIPT="false"
if jq -e '.dependencies["typescript"] or .devDependencies["typescript"]' "$PACKAGE_JSON" > /dev/null 2>&1; then
    HAS_TYPESCRIPT="true"
fi

# Detect build output directory
BUILD_DIR="dist"
if [[ "$FRAMEWORK" == "next.js" ]]; then
    BUILD_DIR=".next"
elif [[ "$FRAMEWORK" == "react" ]]; then
    BUILD_DIR="build"
fi

# Output JSON
cat <<EOF
{
  "framework": "$FRAMEWORK",
  "version": "$VERSION",
  "typescript": $HAS_TYPESCRIPT,
  "buildCommand": "$BUILD_CMD",
  "devCommand": "$DEV_CMD",
  "testCommand": "$TEST_CMD",
  "buildDirectory": "$BUILD_DIR"
}
EOF
