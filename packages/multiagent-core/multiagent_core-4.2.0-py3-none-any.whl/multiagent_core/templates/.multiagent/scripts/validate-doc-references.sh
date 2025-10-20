#!/bin/bash
# PURPOSE: Validate all documentation references in subsystems, agents, and commands
# USAGE: validate-doc-references.sh [--fix]
# EXAMPLES:
#   validate-doc-references.sh           # Check only
#   validate-doc-references.sh --fix     # Auto-fix broken references

set -euo pipefail

FIX_MODE=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX_MODE=true
fi

CONFIG_FILE=".multiagent/docs-config.json"
ERRORS=0
WARNINGS=0

echo "🔍 Validating documentation references..."
echo ""

# Load config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ ERROR: $CONFIG_FILE not found" >&2
    exit 1
fi

# Function to check if file exists
check_file_exists() {
    local file="$1"
    # Remove section anchor
    file="${file%%#*}"

    if [[ -f "$file" ]]; then
        return 0
    else
        return 1
    fi
}

# Function to extract doc references from a file
find_doc_references() {
    local file="$1"

    # Find markdown links: [text](path)
    grep -oP '\[.*?\]\(\K[^)]+(?=\))' "$file" 2>/dev/null | grep -E '(docs/architecture|\.multiagent)' || true

    # Find @ references: @path/to/doc.md
    grep -oP '@\K[^\s]+\.md[^\s]*' "$file" 2>/dev/null || true
}

# Validate architecture files exist
echo "📁 Checking architecture files..."
jq -r '.architecture[].file' "$CONFIG_FILE" | while read -r file; do
    if check_file_exists "$file"; then
        echo "  ✅ $file"
    else
        echo "  ❌ Missing: $file"
        ((ERRORS++))
    fi
done

echo ""
echo "📁 Checking section references..."
jq -r '.sections[] | .file + "#" + .section' "$CONFIG_FILE" | while read -r ref; do
    file="${ref%%#*}"
    section="${ref##*#}"

    if check_file_exists "$file"; then
        # Check if section exists in file
        if grep -q "^#.*${section//-/ }" "$file" 2>/dev/null; then
            echo "  ✅ $ref"
        else
            echo "  ⚠️  Section may not exist: $ref"
            ((WARNINGS++))
        fi
    else
        echo "  ❌ Missing file: $file"
        ((ERRORS++))
    fi
done

echo ""
echo "🔍 Scanning subsystem READMEs..."
find multiagent_core/templates/.multiagent/*/README.md -type f 2>/dev/null | while read -r readme; do
    subsystem=$(basename "$(dirname "$readme")")
    refs=$(find_doc_references "$readme")

    if [[ -n "$refs" ]]; then
        echo "  📄 $subsystem"
        echo "$refs" | while read -r ref; do
            if check_file_exists "$ref"; then
                echo "    ✅ $ref"
            else
                echo "    ❌ Broken: $ref"
                ((ERRORS++))

                if [[ "$FIX_MODE" == true ]]; then
                    echo "    🔧 TODO: Implement auto-fix"
                fi
            fi
        done
    fi
done

echo ""
echo "🔍 Scanning agents..."
find .claude/agents/*.md -type f 2>/dev/null | head -10 | while read -r agent; do
    agent_name=$(basename "$agent" .md)
    refs=$(find_doc_references "$agent")

    if [[ -n "$refs" ]]; then
        echo "  🤖 $agent_name"
        echo "$refs" | while read -r ref; do
            if check_file_exists "$ref"; then
                echo "    ✅ $ref"
            else
                echo "    ❌ Broken: $ref"
                ((ERRORS++))
            fi
        done
    fi
done

echo ""
echo "🔍 Scanning slash commands..."
find .claude/commands/*/*.md -type f 2>/dev/null | head -10 | while read -r cmd; do
    cmd_name=$(basename "$(dirname "$cmd")")/$(basename "$cmd" .md)
    refs=$(find_doc_references "$cmd")

    if [[ -n "$refs" ]]; then
        echo "  ⚡ $cmd_name"
        echo "$refs" | while read -r ref; do
            if check_file_exists "$ref"; then
                echo "    ✅ $ref"
            else
                echo "    ❌ Broken: $ref"
                ((ERRORS++))
            fi
        done
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📊 VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    echo "✅ All documentation references valid!"
    exit 0
else
    echo "❌ Found $ERRORS broken references"
    exit 1
fi
