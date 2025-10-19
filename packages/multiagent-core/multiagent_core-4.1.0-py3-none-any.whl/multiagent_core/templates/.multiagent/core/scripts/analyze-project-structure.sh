#!/usr/bin/env bash
# Script: analyze-project-structure.sh
# Purpose: Detect project stack, framework, and dependencies
# Subsystem: core
# Called by: project-analyzer agent
# Outputs: JSON file with project structure analysis

set -euo pipefail

PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/project-structure.json}"

cd "$PROJECT_DIR" || exit 1

echo "[INFO] Analyzing project structure..."

# Detect package managers and config files
HAS_PACKAGE_JSON=false
HAS_PYPROJECT_TOML=false
HAS_CARGO_TOML=false
HAS_GO_MOD=false

[[ -f package.json ]] && HAS_PACKAGE_JSON=true
[[ -f pyproject.toml ]] && HAS_PYPROJECT_TOML=true
[[ -f Cargo.toml ]] && HAS_CARGO_TOML=true
[[ -f go.mod ]] && HAS_GO_MOD=true

# Detect directories
HAS_SRC=false
HAS_BACKEND=false
HAS_FRONTEND=false
HAS_API=false

[[ -d src ]] && HAS_SRC=true
[[ -d backend ]] && HAS_BACKEND=true
[[ -d frontend ]] && HAS_FRONTEND=true
[[ -d api ]] && HAS_API=true

# Output JSON
cat > "$OUTPUT_FILE" <<JSON
{
  "configFiles": {
    "packageJson": $HAS_PACKAGE_JSON,
    "pyprojectToml": $HAS_PYPROJECT_TOML,
    "cargoToml": $HAS_CARGO_TOML,
    "goMod": $HAS_GO_MOD
  },
  "directories": {
    "src": $HAS_SRC,
    "backend": $HAS_BACKEND,
    "frontend": $HAS_FRONTEND,
    "api": $HAS_API
  },
  "analyzedAt": "$(date -Iseconds)"
}
JSON

echo "✅ Analysis complete: $OUTPUT_FILE"
exit 0
