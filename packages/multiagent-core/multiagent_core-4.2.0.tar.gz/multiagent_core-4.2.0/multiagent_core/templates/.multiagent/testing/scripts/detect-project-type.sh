#!/usr/bin/env bash
# Script: detect-project-type.sh
# Purpose: Identify frontend vs backend vs full-stack project
# Subsystem: testing
# Called by: /testing:test slash command
# Outputs: Project type (frontend, backend, fullstack)

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/project-type.json}"

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Detecting project type in: $PROJECT_DIR"

HAS_FRONTEND=false
HAS_BACKEND=false
FRONTEND_FRAMEWORK=""
BACKEND_FRAMEWORK=""

# Check for frontend indicators
if [ -f "package.json" ]; then
  if grep -qE '"react"|"next"|"vue"|"angular"|"svelte"' package.json 2>/dev/null; then
    HAS_FRONTEND=true
    if grep -q '"next"' package.json; then
      FRONTEND_FRAMEWORK="Next.js"
    elif grep -q '"react"' package.json; then
      FRONTEND_FRAMEWORK="React"
    elif grep -q '"vue"' package.json; then
      FRONTEND_FRAMEWORK="Vue"
    elif grep -q '"angular"' package.json; then
      FRONTEND_FRAMEWORK="Angular"
    elif grep -q '"svelte"' package.json; then
      FRONTEND_FRAMEWORK="Svelte"
    fi
  fi
fi

# Check for backend indicators
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  HAS_BACKEND=true
  BACKEND_FRAMEWORK="Python"
elif [ -f "go.mod" ]; then
  HAS_BACKEND=true
  BACKEND_FRAMEWORK="Go"
elif [ -f "package.json" ]; then
  if grep -qE '"express"|"fastify"|"nestjs"|"koa"' package.json 2>/dev/null; then
    HAS_BACKEND=true
    if grep -q '"express"' package.json; then
      BACKEND_FRAMEWORK="Express"
    elif grep -q '"nestjs"' package.json; then
      BACKEND_FRAMEWORK="NestJS"
    elif grep -q '"fastify"' package.json; then
      BACKEND_FRAMEWORK="Fastify"
    fi
  fi
fi

# Determine project type
PROJECT_TYPE="unknown"
if $HAS_FRONTEND && $HAS_BACKEND; then
  PROJECT_TYPE="fullstack"
elif $HAS_FRONTEND; then
  PROJECT_TYPE="frontend"
elif $HAS_BACKEND; then
  PROJECT_TYPE="backend"
fi

# Generate JSON output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_directory": "$PROJECT_DIR",
  "project_type": "$PROJECT_TYPE",
  "has_frontend": $HAS_FRONTEND,
  "has_backend": $HAS_BACKEND,
  "frontend_framework": "$FRONTEND_FRAMEWORK",
  "backend_framework": "$BACKEND_FRAMEWORK"
}
EOF

echo "✅ Project type detected: $PROJECT_TYPE"
if [ -n "$FRONTEND_FRAMEWORK" ]; then
  echo "   Frontend: $FRONTEND_FRAMEWORK"
fi
if [ -n "$BACKEND_FRAMEWORK" ]; then
  echo "   Backend: $BACKEND_FRAMEWORK"
fi
echo "[INFO] Output saved to: $OUTPUT_FILE"
exit 0
