#!/usr/bin/env bash
# Script: gather-analysis-context.sh
# Purpose: Gather context for enhancement analysis (mechanical data collection)
# Subsystem: enhancement
# Called by: /enhancement:analyze command
# Outputs: JSON with enhancement list, architecture docs, subsystems

set -euo pipefail

# --- Configuration ---
MODE="${1:-all-proposed}"
ENHANCEMENT_ID="${2:-}"
STATUS_FILTER="${3:-}"

# --- Output File ---
CONTEXT_FILE="/tmp/enhancement-analysis-context-$$.json"

# --- Gather Enhancement Files ---
gather_enhancements() {
  local mode=$1
  local id=$2
  local status=$3
  local files=()

  case "$mode" in
    single)
      # Find specific enhancement by ID
      local found=$(find docs/enhancements -type f -name "*${id}*.md" ! -name "*-ANALYSIS.md" 2>/dev/null | head -1)
      if [[ -n "$found" ]]; then
        files+=("$found")
      fi
      ;;
    all-proposed)
      # Find all in proposed folder
      while IFS= read -r file; do
        files+=("$file")
      done < <(find docs/enhancements/01-proposed -type f -name "*.md" 2>/dev/null)
      ;;
    status-filter)
      # Find all in specific status folder
      local status_dir=""
      case "$status" in
        proposed|01-proposed) status_dir="docs/enhancements/01-proposed" ;;
        approved|02-approved) status_dir="docs/enhancements/02-approved" ;;
        in-progress|03-in-progress) status_dir="docs/enhancements/03-in-progress" ;;
        completed|04-completed) status_dir="docs/enhancements/04-completed" ;;
        blocked|05-blocked) status_dir="docs/enhancements/05-blocked" ;;
        rejected|06-rejected) status_dir="docs/enhancements/06-rejected" ;;
      esac

      while IFS= read -r file; do
        files+=("$file")
      done < <(find "$status_dir" -type f -name "*.md" ! -name "*-ANALYSIS.md" 2>/dev/null)
      ;;
  esac

  # Output as JSON array
  printf '%s\n' "${files[@]}" | jq -R . | jq -s .
}

# --- Gather Architecture Docs ---
gather_architecture_docs() {
  local docs=()

  # Main README
  [[ -f "README.md" ]] && docs+=("README.md")

  # Docs README
  [[ -f "docs/README.md" ]] && docs+=("docs/README.md")

  # Architecture docs
  while IFS= read -r file; do
    docs+=("$file")
  done < <(find docs/architecture -type f -name "*.md" 2>/dev/null)

  # Output as JSON array
  printf '%s\n' "${docs[@]}" | jq -R . | jq -s .
}

# --- Gather Subsystem Info ---
gather_subsystems() {
  local subsystems=()

  # Find all subsystem READMEs
  while IFS= read -r readme; do
    local subsystem_name=$(basename $(dirname "$readme"))
    local subsystem_path=$(dirname "$readme")

    # Read first line of README for description
    local description=$(head -1 "$readme" | sed 's/^# //')

    subsystems+=("{\"name\":\"$subsystem_name\",\"path\":\"$subsystem_path\",\"description\":\"$description\"}")
  done < <(find multiagent_core/templates/.multiagent -maxdepth 2 -name "README.md" 2>/dev/null)

  # Output as JSON array
  echo "${subsystems[@]}" | jq -s .
}

# --- Gather Project Metadata ---
gather_project_metadata() {
  local git_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
  local git_status=$(git status --short 2>/dev/null | wc -l)
  local spec_count=$(find specs -maxdepth 1 -type d -name "[0-9]*" 2>/dev/null | wc -l)

  cat <<EOF
{
  "git_branch": "$git_branch",
  "uncommitted_changes": $git_status,
  "active_specs": $spec_count,
  "project_type": "multiagent-framework",
  "analysis_timestamp": "$(date -Iseconds)"
}
EOF
}

# --- Main Execution ---

echo "Gathering analysis context..." >&2
echo "Mode: $MODE" >&2

# Build JSON context
cat > "$CONTEXT_FILE" <<EOF
{
  "mode": "$MODE",
  "enhancement_id": "$ENHANCEMENT_ID",
  "status_filter": "$STATUS_FILTER",
  "enhancements": $(gather_enhancements "$MODE" "$ENHANCEMENT_ID" "$STATUS_FILTER"),
  "architecture_docs": $(gather_architecture_docs),
  "subsystems": $(gather_subsystems),
  "project_metadata": $(gather_project_metadata)
}
EOF

# Validate JSON
if jq empty "$CONTEXT_FILE" 2>/dev/null; then
  echo "✓ Context gathered successfully" >&2
  echo "✓ Enhancement files: $(jq '.enhancements | length' "$CONTEXT_FILE")" >&2
  echo "✓ Architecture docs: $(jq '.architecture_docs | length' "$CONTEXT_FILE")" >&2
  echo "✓ Subsystems: $(jq '.subsystems | length' "$CONTEXT_FILE")" >&2

  # Output file path
  echo "$CONTEXT_FILE"
else
  echo "❌ Error: Invalid JSON generated" >&2
  exit 1
fi
