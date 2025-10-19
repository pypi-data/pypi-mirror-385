#!/usr/bin/env bash
# Script: list-servers.sh
# Purpose: List all MCP servers in the global registry
# Subsystem: mcp
# Called by: /mcp:list slash command
# Outputs: JSON array of server definitions

set -euo pipefail

# --- Configuration ---
REGISTRY_FILE="${1:-$HOME/.multiagent/config/mcp-servers-registry.json}"
OUTPUT_FILE="${2:-/tmp/mcp-servers-list.json}"

# --- Main Logic ---
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "[ERROR] Registry file not found: $REGISTRY_FILE" >&2
    exit 1
fi

echo "[INFO] Reading MCP server registry: $REGISTRY_FILE"

# Extract all servers with their metadata
jq 'to_entries | map({
    name: .key,
    description: .value.description,
    variants: (.value.variants | keys),
    has_local: (if .value.variants.local then true else false end),
    has_remote: (if .value.variants.remote then true else false end)
}) | sort_by(.name)' "$REGISTRY_FILE" > "$OUTPUT_FILE"

SERVER_COUNT=$(jq 'length' "$OUTPUT_FILE")

echo "✅ Found $SERVER_COUNT servers in registry"
echo "📄 Output saved to: $OUTPUT_FILE"
exit 0
